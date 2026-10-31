"""Accepted B1E task corrections preserve source versions and unrelated reviews."""
from collections import Counter
import base64
import csv
from functools import lru_cache
import gzip
import hashlib
import io
import json
from pathlib import Path
import re

import pytest

from scripts.curated_schema import ALLOWED_REVIEW_ACTIONS, ALLOWED_REVIEW_QUEUES
from scripts.paper_exclusions import normalize_doi
from scripts.validate_corpus_quality_audit import decision_rows, load_context, load_queues
from tests.baseline_expectations import CURRENT_CORPUS_COUNTS, CURRENT_TAXONOMY_TOTALS
from tests.corpus_quality_test_helpers import csv_records, published_bytes, published_context

ROOT = Path(__file__).resolve().parents[1]
BASE = "d02b952489b10df438f79ed1b87aee4170ee8aa5"
PUBLISHED = "cc1e1b3d10c2a030e8b2cdda19fc9aaa1c7e8a0f"
TAXONOMY = "data/curated/paper_taxonomy.csv"
PAPERS = "data/curated/papers.csv"
DECISIONS = "data/curated/review_decisions.csv"
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1e_2026_10_17/evidence_manifest.json"
REPORT = "docs/corpus_quality_batch_b_wave_b1e_2026_10_17.md"
AUDIT = "data/raw/corpus_quality_audit_2026_10_04/"
TASK_FIELDS = {"tasks", "tasks_review_reason", "tasks_evidence_tier", "tasks_evidence_source",
               "tasks_evidence_excerpt", "audited_at"}
CASES = {
    "T056": {
        "paper_id": "curated:45cb3642fd138c136139",
        "doi": "10.1609/aaai.v40i8.37553",
        "openalex_url": "https://openalex.org/W7137819524",
        "decision_id": "review:137b41dda95798509659",
        "source": "https://ojs.aaai.org/index.php/AAAI/article/download/37553/41515",
        "source_sha256": "992c7d2e5dc732e19aeda874011554dea8516407d48ab0055974a4c6803664c2",
        "source_pages": 8,
        "research_types": ["method"],
        "metric_tokens": ("75.4", "74.5", "76.5", "75.5"),
    },
    "T345": {
        "paper_id": "curated:0fb6a9c0db904eae726d",
        "doi": "10.1109/tai.2025.3641104",
        "openalex_url": "https://openalex.org/W4378506811",
        "decision_id": "review:0403b6244cb491163707",
        "source": "https://arxiv.org/pdf/2305.13800v2",
        "source_sha256": "cdc62564f93a890b996b14fe29b3d0e037df212a88097b587ecb287bc8891d5d",
        "source_pages": 11,
        "research_types": ["method", "dataset"],
        "metric_tokens": ("0.974", "0.952", "0.913", "0.941"),
    },
}
TARGETS = {case["paper_id"] for case in CASES.values()}
DOI_TO_REVIEW = {case["doi"]: review for review, case in CASES.items()}
EVIDENCE_ONLY_HASHES = {
    "manifest": "8e54a0645a86addafe265efc08bed2e735f7476b8aad01ef452e651161bcc713",
    "report": "768da4d1d6bca7858eeeddb303197381748e9b696b1f0875fea069ba6379940f",
}
# These eight already-published historical receipts are immutable. The live
# taxonomy, compatibility fields, public JSON and decisions are tested by delta.
HISTORICAL_RECEIPT_HASHES = {
    "data/raw/corpus_quality_batch_b_wave_b1a_2026_10_12/evidence_manifest.json":
        "ea455b6de9c3e495fb5893f558804b0dcc2d565b3b26eeb07177cc284530518d",
    "docs/corpus_quality_batch_b_wave_b1a_2026_10_12.md":
        "5c74db551fc104ec7e1bc38956239b2eed5cba722787c11cd59f7d5623efb8a6",
    "data/raw/corpus_quality_batch_b_wave_b1b_2026_10_15/evidence_manifest.json":
        "560da2c20d1f871c8231718ecc62922c810d1d693bc1152cfb590a358e690a4e",
    "docs/corpus_quality_batch_b_wave_b1b_2026_10_15.md":
        "79e474c07a2e493a86411afa0144c030347fe1add6b0d1d3123b612b8ba8ca6c",
    "data/raw/corpus_quality_batch_b_wave_b1c_2026_10_16/evidence_manifest.json":
        "bef6eb0de4eccd2d4cce5282eb78eede8f5b7ccf15a8eb888c41eabfddba9ddf",
    "docs/corpus_quality_batch_b_wave_b1c_2026_10_16.md":
        "9bb7137801590020a53bca6fb94d48cd994d4228b2087041ac02c47f10408109",
    "data/raw/corpus_quality_batch_b_wave_b1d_2026_10_16/evidence_manifest.json":
        "15e5bef92f3de2b7e2ebae33b53588106ec73d8e0d770910fb085f7720116385",
    "docs/corpus_quality_batch_b_wave_b1d_2026_10_16.md":
        "64cec346f5323b626e6cc062cbe4e86cdd0f74a15ff701b4c46702b3a730b84b",
}


def previous(path):
    return published_bytes(BASE, path)


def endpoint_bytes(path):
    # B1E's exact transaction/accounting and recorded source fingerprints belong
    # to its published endpoint. B1F tests check the live one-decision successor;
    # live corpus, carryover, frozen-receipt and NeurIPS guards below remain live.
    return published_bytes(PUBLISHED, path)


def rows(path):
    return csv_records((ROOT / path).read_bytes())


def by_paper(records):
    return {row["paper_id"]: row for row in records}


def selected_rows(records, review_id):
    case = CASES[review_id]
    return [row for row in records if normalize_doi(row.get("doi")) == case["doi"]]


def logical_csv_chunks(raw):
    """Retain exact bytes for each logical CSV record, including embedded CRLF."""
    lines = raw.splitlines(keepends=True)
    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    chunks, start = [], 0
    for _ in reader:
        chunks.append(b"".join(lines[start:reader.line_num]))
        start = reader.line_num
    assert start == len(lines)
    return chunks


def changed_csv_rows_only(path, expected_fields):
    before_raw, after_raw = previous(path), endpoint_bytes(path)
    before_records, after_records = csv_records(before_raw), csv_records(after_raw)
    identity_key = "taxonomy_id" if path == TAXONOMY else "paper_id"
    before = {row[identity_key]: row for row in before_records}
    after = {row[identity_key]: row for row in after_records}
    assert len(before) == len(before_records) and len(after) == len(after_records)
    assert before.keys() == after.keys()
    target_keys = {row[identity_key] for row in before_records if row["paper_id"] in TARGETS}
    assert len(target_keys) == 2
    assert {key for key in before if before[key] != after[key]} == target_keys
    assert [r[identity_key] for r in before_records] == [r[identity_key] for r in after_records]
    for identity in target_keys:
        assert {field for field in before[identity]
                if before[identity][field] != after[identity][field]} == expected_fields
    old_chunks, new_chunks = logical_csv_chunks(before_raw), logical_csv_chunks(after_raw)
    assert len(old_chunks) == len(new_chunks) == len(before_records) + 1
    assert old_chunks[0] == new_chunks[0]
    for old_record, old_raw, new_raw in zip(before_records, old_chunks[1:], new_chunks[1:]):
        if old_record["paper_id"] not in TARGETS:
            assert old_raw == new_raw
        else:
            # Replacement cannot normalize embedded line endings in either row.
            assert old_raw.count(b"\r\n") == new_raw.count(b"\r\n")
            assert old_raw.count(b"\n") == new_raw.count(b"\n")
    return (by_paper(row for row in before_records if row["paper_id"] in TARGETS),
            by_paper(row for row in after_records if row["paper_id"] in TARGETS))


@lru_cache
def packet():
    return json.loads((ROOT / MANIFEST).read_bytes())


@lru_cache
def archived_packet():
    archive = packet()["evidence_only_packet_archives"]["manifest"]
    return json.loads(gzip.decompress(base64.b64decode(archive["payload"], validate=True)))


def terminal_by_review(decisions):
    result = {}
    for decision in decisions:
        match = re.search(r"\bBatch B review ([A-Z]\d{3});", decision["review_note"])
        if match and decision["action"] == "no_action_after_review":
            assert match.group(1) not in result
            result[match.group(1)] = decision["decision_id"]
    return result


# Requirements 1, 2 and 4: both canonical and compatibility fields agree.
@pytest.mark.parametrize("review_id", CASES)
def test_selected_paper_is_detection_only_and_preserves_research_types(review_id):
    case = CASES[review_id]
    for path in (TAXONOMY, PAPERS):
        old = selected_rows(csv_records(previous(path)), review_id)
        new = selected_rows(rows(path), review_id)
        assert len(old) == len(new) == 1
        assert old[0]["paper_id"] == new[0]["paper_id"] == case["paper_id"]
        assert old[0]["tasks"] == "detection;source_attribution"
        assert new[0]["tasks"] == "detection"
        assert new[0]["research_types"] == old[0]["research_types"] == ";".join(case["research_types"])
    current = load_context()["papers"][case["paper_id"]]
    assert current["tasks"] == ["detection"]
    assert current["research_types"] == case["research_types"]


# Requirements 3, 5 and 12: inspect every existing public relationship, not only totals.
@pytest.mark.parametrize("path", PUBLIC)
def test_public_delta_contains_only_selected_tasks_and_dependent_review_provenance(path):
    before, after = json.loads(previous(path)), json.loads(endpoint_bytes(path))
    assert len(before["records"]) == len(after["records"])
    assert [r.get("id") for r in before["records"]] == [r.get("id") for r in after["records"]]
    for review_id, case in CASES.items():
        old_target = selected_rows(before["records"], review_id)
        new_target = selected_rows(after["records"], review_id)
        assert old_target and len(old_target) == len(new_target)
        if path == PUBLIC[0]:
            assert len(new_target) == 1
        assert all(row["in_scope"] and row["tasks"] == ["detection"] for row in new_target)
    changed_reviews = Counter()
    for old, new in zip(before["records"], after["records"]):
        assert normalize_doi(old.get("doi")) == normalize_doi(new.get("doi"))
        review_id = DOI_TO_REVIEW.get(normalize_doi(new.get("doi")))
        if review_id is None:
            assert old == new
            continue
        changed_reviews[review_id] += 1
        assert old["tasks"] == ["detection", "source_attribution"]
        assert new["tasks"] == ["detection"]
        assert new["research_types"] == old["research_types"] == CASES[review_id]["research_types"]
        assert {k: v for k, v in old.items() if k not in {"tasks", "taxonomy_review"}} == {
            k: v for k, v in new.items() if k not in {"tasks", "taxonomy_review"}}
        assert {k: v for k, v in old["taxonomy_review"].items() if k != "tasks"} == {
            k: v for k, v in new["taxonomy_review"].items() if k != "tasks"}
        assert new["taxonomy_review"]["tasks"] == {
            **old["taxonomy_review"]["tasks"],
            "reason": selected_rows(rows(TAXONOMY), review_id)[0]["tasks_review_reason"],
        }
    assert changed_reviews.keys() == CASES.keys()
    for payload in (before, after):
        payload.pop("records")
        payload["metadata"].pop("public_preview_generated_at", None)
    assert before == after


# Requirement 8 and the byte-preserving targeted-edit contract.
def test_only_two_taxonomy_records_and_tasks_only_compatibility_fields_change():
    before, after = changed_csv_rows_only(TAXONOMY, TASK_FIELDS)
    changed_csv_rows_only(PAPERS, {"tasks"})
    for review_id, case in CASES.items():
        record = after[case["paper_id"]]
        assert record["tasks_status"] == before[case["paper_id"]]["tasks_status"] == "reviewed"
        assert record["tasks_evidence_tier"] == "primary_paper"
        assert record["tasks_evidence_source"] == case["source"]
        assert review_id in record["tasks_review_reason"] and "T1" in record["tasks_review_reason"]
        assert record["audited_at"] == "2026-10-18"


# Requirement 6: the published B1E endpoint appended exactly two decisions.
def test_exactly_two_accepted_terminal_decisions_append_without_duplicate_ids():
    before_raw, after_raw = previous(DECISIONS), endpoint_bytes(DECISIONS)
    assert after_raw.startswith(before_raw)
    before, after = csv_records(before_raw), csv_records(after_raw)
    assert after[:len(before)] == before
    added = after[len(before):]
    assert len(added) == 2
    assert {r["decision_id"] for r in added} == {case["decision_id"] for case in CASES.values()}
    assert len({r["decision_id"] for r in after}) == len(after)
    for review_id, case in CASES.items():
        chosen = selected_rows(added, review_id)
        assert len(chosen) == 1
        record = chosen[0]
        assert record["decision_id"] == case["decision_id"]
        assert record["target_type"] == "paper" and record["openalex_url"] == case["openalex_url"]
        assert record["review_queue"] == "other" and record["review_queue"] in ALLOWED_REVIEW_QUEUES
        assert record["action"] == "no_action_after_review" and record["action"] in ALLOWED_REVIEW_ACTIONS
        assert record["created_by"] == "maintainer-approved-batch-b-b1e"
        assert record["created_at"] == record["updated_at"] == "2026-10-18T00:00:00Z"
        note = record["review_note"]
        assert f"Batch B review {review_id};" in note
        for token in ("DETECTION_ONLY", "PROPOSE_CORRECTION_ACCEPTED", "source_attribution", "detection", case["source"]):
            assert token in note
        assert all(token in note for token in case["metric_tokens"])
    assert terminal_by_review(after) == {
        **terminal_by_review(before), **{review_id: case["decision_id"] for review_id, case in CASES.items()}}


# Requirement 7: the correction must not turn an author version into publisher-final proof.
def test_t345_version_boundary_and_work_identity_are_preserved_explicitly():
    original = next(r for r in archived_packet()["records"] if r["review_id"] == "T345")
    current = next(r for r in packet()["records"] if r["review_id"] == "T345")
    provenance = current["source_provenance"]
    assert provenance == original["source_provenance"]
    assert provenance["primary_url"] == CASES["T345"]["source"]
    assert provenance["publisher_final_equivalence_verified"] is False
    assert "2305.13800v2" in provenance["version"] and "2025-04-30" in provenance["version"]
    assert current["adjudication"]["version_limitation"] == provenance["version_limitation"]
    assert "publisher-final" in provenance["version_limitation"]
    identity = current["canonical_identity"]
    canonical = selected_rows(rows(PAPERS), "T345")[0]
    assert identity["paper_id"] == canonical["paper_id"] == CASES["T345"]["paper_id"]
    assert identity["doi"] == canonical["doi"] == CASES["T345"]["doi"]
    assert identity["arxiv_id"] == canonical["arxiv_id"] == "2305.13800"
    assert identity["title"] == canonical["title"]
    assert identity["authors"] == [name.strip() for name in canonical["authors"].split(";")]
    assert canonical["publication_type"] == "journal" and canonical["year"] == "2025"
    adjudication_note = selected_rows(rows(DECISIONS), "T345")[0]["review_note"].lower()
    assert "v2" in adjudication_note and "unverified" in adjudication_note
    report = (ROOT / REPORT).read_text(encoding="utf-8").lower()
    assert "arxiv" in report and "v2" in report and "unverified" in report


# Requirements 9 and 10: action-level pending status must not become paper-level closure.
@pytest.mark.parametrize("review_id", ["T608", "T526", "P526"])
def test_unselected_pending_actions_and_their_public_records_remain_exact(review_id):
    ledger = [r for r in decision_rows(load_queues()) if r.get("batch") == "B"]
    selected = [r for r in ledger if r["review_id"] == review_id]
    assert len(selected) == 1
    assert review_id not in terminal_by_review(rows(DECISIONS))
    pid = selected[0]["paper_id"]
    old, new = published_context(BASE), load_context()
    assert pid in old["papers"] and new["papers"][pid] == old["papers"][pid]
    assert new["taxonomy"][pid] == old["taxonomy"][pid]


# Requirement 11: derive the distinct affected-paper count from the actual ledger.
def test_batch_b_accounting_recomputes_after_exactly_two_action_resolutions():
    ledger = [r for r in decision_rows(load_queues()) if r.get("batch") == "B"]
    assert len(ledger) == 159 and len({r["paper_id"] for r in ledger}) == 148
    old_resolved = terminal_by_review(csv_records(previous(DECISIONS)))
    new_resolved = terminal_by_review(csv_records(endpoint_bytes(DECISIONS)))
    assert set(new_resolved) - set(old_resolved) == set(CASES)
    assert set(old_resolved) == {"L013", "P139", "P153", "P490", "R137", "R611", "T579"}
    old_pending = [r for r in ledger if r["review_id"] not in old_resolved]
    new_pending = [r for r in ledger if r["review_id"] not in new_resolved]
    public = published_context(PUBLISHED)["papers"]
    old_public = published_context(BASE)["papers"]
    old_active = [r for r in old_pending if r["paper_id"] in old_public]
    active = [r for r in new_pending if r["paper_id"] in public]
    inactive = [r for r in new_pending if r["paper_id"] not in public]
    assert len(old_pending) == 152 and len(old_active) == 150
    assert len({r["paper_id"] for r in old_active}) == 139
    assert len(new_pending) == 150 and len(active) == 148
    assert {r["review_id"] for r in inactive} == {"L015", "P562"}
    assert {"T608", "T526", "P526"} <= {r["review_id"] for r in active}
    assert {r["review_id"] for r in active}.isdisjoint(CASES)
    assert all(sum(r["paper_id"] == case["paper_id"] for r in ledger) == 1 for case in CASES.values())
    account = packet()["batch_b_accounting"]
    assert account["historical_actions"] == len(ledger)
    assert account["historical_papers"] == len({r["paper_id"] for r in ledger})
    assert account["historical_unresolved_actions"] == len(new_pending)
    assert account["active_public_unresolved_actions"] == len(active)
    assert account["active_public_unresolved_papers"] == len({r["paper_id"] for r in active})
    resolved = account.get("resolved_review_ids", account.get("resolved_original_review_ids"))
    assert resolved == sorted(new_resolved)
    assert account["active_public_unresolved_review_ids"] == [r["review_id"] for r in active]


# Requirements 5 and 13: count preferred public identities, never repeated map rows.
def test_current_taxonomy_totals_and_exact_two_label_delta_are_recomputed():
    old, current = published_context(BASE), published_context(PUBLISHED)
    assert old["counts"] == current["counts"] == CURRENT_CORPUS_COUNTS == {
        "public": 674, "formal": 557, "mapped": 613, "unmapped": 61,
        "relationship_rows": 1410, "unique_paper_institution_pairs": 1410}
    assert list(old["papers"]) == list(current["papers"])
    assert old["pairs"] == current["pairs"] and all(n == 1 for n in current["pairs"].values())
    def totals(context):
        return Counter(label for record in context["papers"].values()
                       for dim in ("tasks", "research_types") for label in record[dim])
    before, after = totals(old), totals(current)
    assert before - after == {"source_attribution": 2} and not after - before
    assert after == {
        "detection": 621, "source_attribution": 84, "localization": 45,
        "method": 579, "dataset": 134, "benchmark": 90, "survey": 21, "analysis_study": 81}
    assert packet()["corpus_after"] == current["counts"]
    assert packet()["taxonomy_after"] == after
    assert not any("source_attribution" in current["papers"][pid]["tasks"] for pid in TARGETS)
    current_aliases = {row["taxonomy_id"]: pid for pid, row in current["taxonomy"].items()}
    assert old["taxonomy_to_public_id"] == current_aliases
    # Keep the exact B1E transaction historical and the successor corpus live.
    live = load_context()
    assert live["counts"] == CURRENT_CORPUS_COUNTS
    assert totals(live) == CURRENT_TAXONOMY_TOTALS
    assert live["pairs"] == current["pairs"]


# Requirement 12, including authoritative identity rows hidden from any public view.
@pytest.mark.parametrize("path", [
    "data/curated/paper_exclusions.csv", "data/curated/publication_overrides.csv",
    "data/curated/paper_arxiv_links.csv", "data/curated/paper_version_merges.csv",
    "data/curated/venue_aliases.csv", "data/curated/author_institution_mappings.csv",
    "data/curated/institution_author_overrides.csv", "data/curated/institutions.csv",
    "data/curated/institution_locations.csv", "data/curated/institution_aliases.csv",
    "data/curated/institution_hierarchy.csv",
])
def test_unrelated_authoritative_metadata_identity_and_relationship_files_are_byte_exact(path):
    # These two files now have separately authorized B4 publication additions.
    # Preserve the original B1E transaction assertion at its published endpoint;
    # all other identity/institution/relationship guards remain live.
    publication_paths = {'data/curated/publication_overrides.csv', 'data/curated/venue_aliases.csv'}
    observed = endpoint_bytes(path) if path in publication_paths else (ROOT / path).read_bytes()
    assert observed == previous(path)


def test_original_evidence_archives_retrievals_and_scientific_findings_survive_adjudication():
    archives = packet()["evidence_only_packet_archives"]
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
    original = archived_packet()
    assert original["baseline"]["commit"] == BASE
    assert original["scope"]["authoritative_changes"] == original["scope"]["review_actions_closed"] == 0
    assert packet()["scope"]["authoritative_changes"] == packet()["scope"]["review_actions_closed"] == 2
    for field in ("source_files", "retrieval_accounting", "locked_policy", "operational_source_files"):
        assert packet()[field] == original[field]
    retrieval = packet()["retrieval_accounting"]
    assert retrieval["successful_full_manuscripts_total"] == 2
    assert retrieval["successful_full_manuscripts_by_review"] == retrieval["full_text_attempts_by_review"] == {"T056": 1, "T345": 1}
    assert retrieval["automatic_retries"] == retrieval["failed_full_text_attempts"] == retrieval["alternate_manuscript_versions"] == 0
    assert {r["review_id"] for r in packet()["records"]} == set(CASES)
    for review_id, case in CASES.items():
        old = next(r for r in original["records"] if r["review_id"] == review_id)
        new = next(r for r in packet()["records"] if r["review_id"] == review_id)
        for field in ("canonical_identity", "original_review", "original_intake_question",
                      "other_original_actions_not_adjudicated", "source_provenance", "scientific_findings",
                      "provisional_outcome", "proposed_tasks", "confidence"):
            assert new[field] == old[field]
        assert new["source_provenance"]["sha256"] == case["source_sha256"]
        assert new["source_provenance"]["pages"] == case["source_pages"]
        assert new["full_text_examined"] is new["scientifically_sufficient"] is True
        assert new["maintainer_acceptance_pending"] is False
        assert new["authoritative_changes_applied"] is new["formal_review_action_closed"] is True
        adjudication = new["adjudication"]
        assert adjudication["accepted_outcome"] == new["provisional_outcome"] == "DETECTION_ONLY"
        assert adjudication["applied"] is True
        assert adjudication["tasks_before"] == ["detection", "source_attribution"]
        assert adjudication["tasks_after"] == ["detection"]
        assert adjudication["taxonomy_before"] == selected_rows(csv_records(previous(TAXONOMY)), review_id)[0]
        assert adjudication["taxonomy_after"] == selected_rows(rows(TAXONOMY), review_id)[0]
        assert set(adjudication["changed_fields"]) == TASK_FIELDS
        assert adjudication["review_decision"] == selected_rows(rows(DECISIONS), review_id)[0]
        assert new["post_adjudication_public_state"] == load_context()["papers"][case["paper_id"]]
    # source_files fingerprints describe d02; current_source_sha256 describes
    # the published B1E endpoint, not files changed by a later approved wave.
    historic_sources = {entry["path"]: entry["sha256"] for entry in original["source_files"]}
    assert packet()["current_source_sha256"].keys() == historic_sources.keys()
    for path, historical_sha in historic_sources.items():
        assert hashlib.sha256(previous(path)).hexdigest() == historical_sha
        assert hashlib.sha256(endpoint_bytes(path)).hexdigest() == packet()["current_source_sha256"][path]


# Requirement 14: fixed fingerprints are confined to genuinely historical artifacts.
@pytest.mark.parametrize("path,expected", HISTORICAL_RECEIPT_HASHES.items())
def test_all_eight_prior_batch_b_receipts_remain_immutable(path, expected):
    assert hashlib.sha256(previous(path)).hexdigest() == expected
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
    assert (ROOT / path).read_bytes() == previous(path)


@pytest.mark.parametrize("filename", ["unmapped_papers.json", "taxonomy_review.json", "relationship_review.json",
                                     "publication_metadata_review.json", "batch_c_policy_decisions.json"])
def test_original_pending_review_ledgers_and_locked_policy_remain_immutable(filename):
    path = AUDIT + filename
    assert (ROOT / path).read_bytes() == previous(path)


def test_separate_39_paper_import_inventory_and_thirteen_batch_c_debts_are_unchanged():
    inventory = packet()["separate_import_review_inventory"]
    assert inventory == archived_packet()["separate_import_review_inventory"]
    imported = inventory["imported_affiliation_debts"]["records"]
    assert len(imported) == inventory["imported_affiliation_debts"]["count"] == 39
    old, current = published_context(BASE), load_context()
    for record in imported:
        pid = record["paper_id"]
        assert current["papers"][pid] == old["papers"][pid]
        assert current["taxonomy"][pid] == old["taxonomy"][pid]
    for path in (
        "data/processed/literature51_2026_10_16/plan.json",
        "data/processed/literature51_2026_10_16/followup/review.json",
        "data/processed/literature51_2026_10_16/followup/receipt.json",
        "data/processed/literature51_2026_10_16/main_integration/manifest.json",
        "docs/literature51_main_integration_2026_10_17.md",
        "data/raw/corpus_quality_batch_c_closeout_2026_10_11/evidence_manifest.json",
        "docs/corpus_quality_batch_c_closeout_2026_10_11.md",
    ):
        assert (ROOT / path).read_bytes() == previous(path)


def test_all_49_frozen_neurips_artifacts_remain_byte_exact():
    receipt = json.loads((ROOT / "data/raw/systematic_gap_migration_2026_10_03/baseline.json").read_bytes())
    assert len(receipt["frozen_sha256"]) == 49
    for path, expected in receipt["frozen_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
