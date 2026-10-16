"""Accepted P490 scope exclusion keeps bibliography, history and independent reviews."""
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
import subprocess

import pytest

from scripts.curated_export import PaperIdentityCache, PaperIdentityIndex
from scripts.curated_schema import ALLOWED_REVIEW_ACTIONS, ALLOWED_REVIEW_QUEUES
from scripts.paper_exclusions import (build_active_exclusion_index, filter_public_output_pair,
                                     normalize_doi, read_exclusion_rows, record_is_excluded)
from scripts.review_decisions import read_review_decisions
from scripts.validate_corpus_quality_audit import decision_rows, load_context, load_queues
from scripts.venue_audit import confirmation_fingerprint
from tests.baseline_expectations import CURRENT_CORPUS_COUNTS, CURRENT_TAXONOMY_TOTALS

ROOT = Path(__file__).resolve().parents[1]
BASE = "65e9422764c34eaad1d151fff2895e6c7503835f"
DOI = "10.1080/21670811.2024.2331769"
P490 = "doi:" + DOI
OPENALEX = "https://openalex.org/W4394571198"
TITLE = "Generative Visual AI in News Organizations: Challenges, Opportunities, Perceptions, and Policies"
T526 = "curated:e058b4e851ac44180d82"
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
AUDIT = "data/raw/corpus_quality_audit_2026_10_04/"
MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1c_2026_10_16/evidence_manifest.json"
CANDIDATES = "data/processed/openalex_candidate_papers.csv"
CANDIDATES_SHA256 = "9d6f0ff95f891a3f93816f34d828d23b12245567b243562b2181ba4dee839d1e"


@lru_cache
def previous(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def csvrows(raw):
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline="")))


def rows(path):
    return csvrows((ROOT / path).read_bytes())


def matches(record):
    return normalize_doi(record.get("doi")) == DOI


@lru_cache
def identity_index():
    return PaperIdentityIndex(csvrows(previous("data/curated/paper_taxonomy.csv")), PaperIdentityCache())


def canonical_id(record):
    found = identity_index().matches(record)
    assert len(found) == 1, record.get("title")
    return record.get("paper_id") or found[0]["taxonomy_id"]


def packet():
    return json.loads((ROOT / MANIFEST).read_bytes())


def p490_decisions():
    return [row for row in read_review_decisions(ROOT / "data/curated/review_decisions.csv") if matches(row)]


def selected_exclusion():
    selected = [row for row in read_exclusion_rows(ROOT / "data/curated/paper_exclusions.csv") if matches(row)]
    assert len(selected) == 1
    return selected[0]


def test_exactly_one_reversible_exclusion_appends_with_prior_bytes_preserved():
    path = "data/curated/paper_exclusions.csv"
    old, new = previous(path), (ROOT / path).read_bytes()
    assert new.startswith(old)
    added = rows(path)[len(csvrows(old)):]
    assert added == [selected_exclusion()]
    row = added[0]
    assert row["paper_id"] == ""  # Candidate identity; do not fabricate a curated paper ID.
    assert row["title"] == TITLE and row["year"] == "2024"
    assert row["openalex_url"] == OPENALEX
    assert row["reason"] == "out_of_scope"
    assert all(row[key] == "true" for key in ("is_active", "excluded_from_public_preview", "excluded_from_map"))
    assert not row["restored_at"] and not row["restore_note"]
    assert "EXCLUDE_OUT_OF_SCOPE" in row["review_note"]
    active = build_active_exclusion_index([row])
    restored = build_active_exclusion_index([{**row, "is_active": "false"}])
    aliases = [{"doi": DOI.upper()}, {"doi": "https://doi.org/" + DOI}, {"openalex_url": OPENALEX}]
    assert all(record_is_excluded(alias, active) for alias in aliases)
    assert all(not record_is_excluded(alias, restored) for alias in aliases)


@pytest.mark.parametrize("path,removed_count", [(PUBLIC[0], 1), (PUBLIC[1], 3)])
def test_public_delta_removes_only_p490_and_preserves_every_retained_record(path, removed_count):
    old = json.loads(previous(path))
    new = json.loads((ROOT / path).read_bytes())
    removed = [row for row in old["records"] if matches(row)]
    assert len(removed) == removed_count
    assert not any(matches(row) for row in new["records"])
    # Exact ordered equality checks every retained paper, author, institution,
    # relationship identity, task, publication field and review diagnostic.
    assert new["records"] == [row for row in old["records"] if not matches(row)]
    for payload in (old, new):
        payload.pop("records")
        payload["metadata"].pop("public_preview_generated_at", None)
    assert old == new


def test_exclusion_filter_is_reversible_and_exactly_removes_three_existing_pairs():
    papers, maps = [json.loads(previous(path))["records"] for path in PUBLIC]
    selected = selected_exclusion()
    filtered, filtered_maps, impact = filter_public_output_pair(papers, maps, [selected])
    assert filtered == [row for row in papers if not matches(row)]
    assert filtered_maps == [row for row in maps if not matches(row)]
    assert impact == {"active_exclusion_public_papers_removed": 1, "active_exclusion_map_records_removed": 3}
    restored, restored_maps, impact = filter_public_output_pair(papers, maps, [{**selected, "is_active": "false"}])
    assert restored == papers and restored_maps == maps
    assert set(impact.values()) == {0}
    removed_pairs = {(canonical_id(row), row["institution_id"]) for row in maps if matches(row)}
    assert len(removed_pairs) == 3 and {pid for pid, _ in removed_pairs} == {P490}


@pytest.mark.parametrize("path", [
    "data/curated/papers.csv", "data/curated/paper_taxonomy.csv",
    "data/curated/publication_overrides.csv", "data/curated/paper_arxiv_links.csv",
    "data/curated/paper_version_merges.csv", "data/curated/venue_aliases.csv",
    "data/curated/author_institution_mappings.csv", "data/curated/institution_author_overrides.csv",
    "data/curated/institutions.csv", "data/curated/institution_locations.csv",
    "data/curated/institution_aliases.csv", "data/curated/institution_hierarchy.csv",
])
def test_canonical_bibliography_taxonomy_authors_and_institutions_are_unchanged(path):
    assert (ROOT / path).read_bytes() == previous(path)


def test_p490_historical_taxonomy_and_source_identity_survive_without_replacement_task():
    source = (ROOT / CANDIDATES).read_bytes()
    assert hashlib.sha256(source).hexdigest() == CANDIDATES_SHA256
    source_rows = [row for row in csvrows(source) if matches(row)]
    assert len(source_rows) == 1
    assert source_rows[0]["title"] == TITLE
    taxonomy = [row for row in rows("data/curated/paper_taxonomy.csv") if matches(row)]
    historical = [row for row in csvrows(previous("data/curated/paper_taxonomy.csv")) if matches(row)]
    assert len(taxonomy) == 1 and taxonomy == historical
    assert taxonomy[0]["taxonomy_id"] == P490
    assert taxonomy[0]["tasks"] == "detection" and taxonomy[0]["research_types"] == "analysis_study"
    context = load_context()
    assert P490 not in context["papers"] and P490 not in context["taxonomy"]


def test_scope_and_publication_decisions_are_distinct_existing_schema_rows_without_duplicates():
    path = "data/curated/review_decisions.csv"
    old, new = previous(path), (ROOT / path).read_bytes()
    assert new.startswith(old)
    added = rows(path)[len(csvrows(old)):]
    assert len(added) == 2 and added == p490_decisions()
    assert len({row["decision_id"] for row in added}) == 2
    by_action = {row["action"]: row for row in added}
    assert set(by_action) == {"exclude_paper_scope", "no_action_after_review"} <= ALLOWED_REVIEW_ACTIONS
    scope, publication = by_action["exclude_paper_scope"], by_action["no_action_after_review"]
    assert scope["review_queue"] == "other"
    assert publication["review_queue"] == "publication_venues"
    for row in added:
        assert row["review_queue"] in ALLOWED_REVIEW_QUEUES
        assert row["target_type"] == "paper" and row["title"] == TITLE and row["year"] == "2024"
    assert "EXCLUDE_OUT_OF_SCOPE" in scope["review_note"]
    assert "Batch B review P490;" in publication["review_note"]
    assert "SUPPORTED_NO_CHANGE" in publication["review_note"]
    assert "Batch B review P490;" not in scope["review_note"]  # Scope is not another historical ledger action.
    all_decisions = read_review_decisions(ROOT / path)
    assert all(sum(row["decision_id"] == added_row["decision_id"] for row in all_decisions) == 1 for added_row in added)


def test_journal_confirmation_is_bounded_to_existing_venue_state_without_abbreviation():
    before = next(row for row in json.loads(previous(PUBLIC[0]))["records"] if matches(row))
    assert before["venue_name"] == "Digital Journalism" and before["venue_acronym"] == ""
    publication = next(row for row in p490_decisions() if row["action"] == "no_action_after_review")
    marker = re.findall(r"\[venue-state:([a-f0-9]{64})\]", publication["review_note"])
    assert marker == [confirmation_fingerprint(before)]
    assert marker == ["6c3b88ab37c75be424e82518aee11c07f46283b7444f6854396973b92d5ed009"]
    assert "No bibliographic fields changed" in publication["review_note"]


def test_first_online_and_issue_year_evidence_remain_separate_without_year_rewrite():
    path = "data/raw/venue_audit_crossref/fb462d8cd1b38ab48f4f.json"
    assert (ROOT / path).read_bytes() == previous(path)
    deposit = json.loads((ROOT / path).read_bytes())["response"]["message"]
    assert deposit["DOI"].lower() == DOI
    assert deposit["container-title"] == deposit["short-container-title"] == ["Digital Journalism"]
    assert deposit["published-online"]["date-parts"] == [[2024, 4, 8]]
    assert deposit["published-print"]["date-parts"][0][0] == 2025
    assert (deposit["volume"], deposit["issue"], deposit["page"]) == ("13", "10", "1693-1714")
    baseline = next(row for row in json.loads(previous(PUBLIC[0]))["records"] if matches(row))
    assert baseline["year"] == baseline["publication_year"] == 2024
    assert baseline["publication_date"] == "2024-04-08"
    publication = next(row for row in p490_decisions() if row["action"] == "no_action_after_review")
    assert "issue year 2025" in publication["review_note"]
    assert "final-issue PDF equivalence remains unverified" in publication["review_note"]


@pytest.mark.parametrize("path", PUBLIC)
def test_t526_public_tasks_and_bibliography_remain_exact(path):
    before = [row for row in json.loads(previous(path))["records"] if canonical_id(row) == T526]
    after = [row for row in json.loads((ROOT / path).read_bytes())["records"] if canonical_id(row) == T526]
    assert before and before == after
    assert all(row["tasks"] == ["detection"] and row["research_types"] == ["method"] for row in after)


def test_t526_and_p526_have_no_new_authoritative_decision_and_original_evidence_limit_remains():
    decisions = read_review_decisions(ROOT / "data/curated/review_decisions.csv")
    baseline = csvrows(previous("data/curated/review_decisions.csv"))
    assert [row for row in decisions if normalize_doi(row["doi"]) == "10.1109/wifs61860.2024.10810686"] == [
        row for row in baseline if normalize_doi(row["doi"]) == "10.1109/wifs61860.2024.10810686"]
    t526 = next(row for row in packet()["records"] if row["review_id"] == "T526")
    assert t526["provisional_disposition"] == "EVIDENCE_STILL_INSUFFICIENT"
    assert t526["scientifically_sufficient"] is False and t526["remediation_applied"] is False
    assert t526["formal_review_action_closed"] is False
    assert t526["full_text_examined"] is False and t526["proposed_task_taxonomy"] is None
    assert t526["version_limitations"]
    assert "P526" in {row["review_id"] for row in t526["independent_batch_b_actions"]}


def test_counts_recompute_with_only_p490_detection_and_analysis_contributions_removed():
    context = load_context()
    assert context["counts"] == CURRENT_CORPUS_COUNTS == {
        "public": 635, "formal": 527, "mapped": 613, "unmapped": 22,
        "relationship_rows": 1410, "unique_paper_institution_pairs": 1410}
    old = Counter(label for row in json.loads(previous(PUBLIC[0]))["records"]
                  for dimension in ("tasks", "research_types") for label in row[dimension])
    new = Counter(label for row in context["papers"].values()
                  for dimension in ("tasks", "research_types") for label in row[dimension])
    assert new == CURRENT_TAXONOMY_TOTALS
    assert old - new == {"detection": 1, "analysis_study": 1} and not new - old


def test_review_accounting_retains_original_159_questions_and_resolves_p490_only_once():
    ledger = [row for row in decision_rows(load_queues()) if row.get("batch") == "B"]
    assert len(ledger) == 159 and len({row["paper_id"] for row in ledger}) == 148
    p490 = [row for row in ledger if row["paper_id"] == P490]
    assert len(p490) == 1 and p490[0]["review_id"] == "P490"
    terminal = read_review_decisions(ROOT / "data/curated/review_decisions.csv")
    closed = set()
    for decision in terminal:
        match = re.search(r"\bBatch B review ([A-Z]\d{3});", decision["review_note"])
        if match and decision["action"] == "no_action_after_review":
            closed.add(match.group(1))
    assert closed == {"R137", "R611", "L013", "P139", "P153", "P490"}
    public = set(load_context()["papers"])
    pending = [row for row in ledger if row["paper_id"] in public and row["review_id"] not in closed]
    assert len(pending) == 151 and len({row["paper_id"] for row in pending}) == 140
    assert {row["review_id"] for row in pending if row["paper_id"] == T526} == {"T526", "P526"}
    inactive_pending = [row for row in ledger if row["paper_id"] not in public and row["review_id"] not in closed]
    assert {row["review_id"] for row in inactive_pending} == {"L015", "P562"}
    assert len(ledger) - len(closed) == 153


@pytest.mark.parametrize("filename", ["unmapped_papers.json", "taxonomy_review.json", "relationship_review.json", "publication_metadata_review.json", "batch_c_policy_decisions.json"])
def test_original_review_ledgers_and_locked_policy_receipts_are_unchanged(filename):
    assert (ROOT / (AUDIT + filename)).read_bytes() == previous(AUDIT + filename)


@pytest.mark.parametrize("path", [
    "data/raw/corpus_quality_batch_b_wave_b1a_2026_10_12/evidence_manifest.json",
    "docs/corpus_quality_batch_b_wave_b1a_2026_10_12.md",
    "data/raw/corpus_quality_batch_b_wave_b1b_2026_10_15/evidence_manifest.json",
    "docs/corpus_quality_batch_b_wave_b1b_2026_10_15.md",
    "data/raw/corpus_quality_batch_c_closeout_2026_10_11/evidence_manifest.json",
    "docs/corpus_quality_batch_c_closeout_2026_10_11.md",
])
def test_all_published_b1a_b1b_and_batch_c_debt_receipts_remain_frozen(path):
    assert (ROOT / path).read_bytes() == previous(path)


def test_initial_failed_retrievals_and_original_evidence_archives_remain_recoverable():
    evidence = packet()
    assert len(evidence["records"]) == 2 and {row["review_id"] for row in evidence["records"]} == {"P490", "T526"}
    history = evidence["retrieval_history"]
    assert history["retries"] == 0 and len(history["records"]) == 2
    failures = {row["review_id"]: row for row in history["records"]}
    assert failures["P490"]["http_status"] == 403
    assert failures["T526"]["http_status"] is None
    assert all(row["outcome"] == "FULL_TEXT_RETRIEVAL_FAILED" for row in failures.values())
    assert {key: archive["sha256"] for key, archive in evidence["original_evidence_packet_archives"].items()} == {
        "manifest": "875f599687d6b356728f7d7a44819e445f8fa5740e59f05a04b1d85607445f25",
        "report": "cecdfeced7965531d5394e3cb3c0001fce759b318ee50d564c112c90538b88b9"}
    for archive in evidence["original_evidence_packet_archives"].values():
        assert archive["encoding"] == "gzip+base64"
        compressed = base64.b64decode(archive["payload"], validate=True)
        assert hashlib.sha256(compressed).hexdigest() == archive["compressed_sha256"]
        original = gzip.decompress(compressed)
        assert len(original) == archive["bytes"] and hashlib.sha256(original).hexdigest() == archive["sha256"]


def test_all_49_frozen_neurips_artifacts_remain_byte_identical():
    receipt = json.loads((ROOT / "data/raw/systematic_gap_migration_2026_10_03/baseline.json").read_bytes())
    assert len(receipt["frozen_sha256"]) == 49
    for path, expected in receipt["frozen_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path


def test_final_packet_reconciles_separate_accepted_decisions_archive_fidelity_and_public_delta():
    evidence = packet()
    assert evidence["baseline"]["commit"] == BASE
    assert evidence["phase"] == "MAINTAINER_APPROVED_P490_ADJUDICATION"
    assert evidence["evidence_only"] is False
    assert evidence["scope"]["adjudicated_review_ids"] == ["P490"]
    assert evidence["scope"]["scope_exclusions_applied"] == 1
    assert evidence["scope"]["bounded_journal_no_change_resolutions"] == 1
    assert evidence["scope"]["authoritative_rows_added"] == {"exclusions": 1, "review_decisions": 2}
    assert evidence["scope"]["new_scientific_evidence_retrieved_during_adjudication"] == 0
    assert evidence["scope"]["T526_unchanged"] is True and evidence["scope"]["P526_pending"] is True

    original_hashes = {
        "manifest": "756118eee1ce37cc5d19772434305a3549b9071941ae7cf0e3c73c899e5a7466",
        "report": "e76a7494a3e1521bd95c43ed79a7ba052613a3ac5c39c034cc6d757c372f535a"}
    recovered = {}
    assert set(evidence["pre_adjudication_followup_archives"]) == set(original_hashes)
    for key, expected_hash in original_hashes.items():
        archive = evidence["pre_adjudication_followup_archives"][key]
        assert archive["encoding"] == "gzip+base64" and archive["gzip_mtime"] == 0
        raw = gzip.decompress(base64.b64decode(archive["content"], validate=True))
        assert hashlib.sha256(raw).hexdigest() == archive["sha256"] == expected_hash
        assert len(raw) == archive["uncompressed_bytes"]
        recovered[key] = raw
    original = json.loads(recovered["manifest"])
    for key in ("original_evidence_packet_archives", "retrieval_history", "source_files", "follow_up"):
        assert evidence[key] == original[key]
    assert evidence["pre_adjudication_followup_snapshot"] == {
        key: original[key] for key in ("scope", "accounting", "validation", "integrity",
                                      "corpus_counts", "taxonomy_counts", "final_git_requirements")}
    prior_cases = {row["review_id"]: row for row in original["records"]}
    cases = {row["review_id"]: row for row in evidence["records"]}
    assert len(evidence["records"]) == 2 and cases.keys() == prior_cases.keys() == {"P490", "T526"}
    assert cases["T526"] == prior_cases["T526"]  # Complete unreviewed protocol/version limitation survives.
    p490 = cases["P490"]
    for key in ("canonical_identity", "original_review", "exact_original_review_question",
                "source_provenance", "method_and_evaluation", "version_limitations", "rationale"):
        assert p490[key] == prior_cases["P490"][key]
    assert p490["accepted_scope_disposition"] == "EXCLUDE_OUT_OF_SCOPE"
    assert p490["maintainer_acceptance_pending"] is False
    assert p490["authoritative_remediation_authorized"] is p490["remediation_applied"] is True
    assert p490["formal_review_action_closed"] is True
    scope, publication = p490["scope_adjudication"], p490["publication_review_adjudication"]
    actual = {row["decision_id"]: row for row in p490_decisions()}
    assert set(actual) == {"review:d8e6166bd21581fdf6c9", "review:3bd38e999af3d8ded107"}
    assert scope["review_decision"] == actual["review:d8e6166bd21581fdf6c9"]
    assert scope["exclusion"] == selected_exclusion()
    assert scope["accepted"] is scope["applied"] is scope["reversible"] is True
    assert scope["original_review_id_created"] is False
    assert scope["original_publication_question_resolved_by_this_scope_decision"] is False
    assert publication["review_decision"] == actual["review:3bd38e999af3d8ded107"]
    assert publication["review_id"] == "P490" and publication["accepted_outcome"] == "SUPPORTED_NO_CHANGE"
    assert publication["accepted"] is publication["resolved"] is True and publication["bibliographic_changes"] == 0
    assert publication["venue_confirmation_fingerprint"] == confirmation_fingerprint(
        next(row for row in json.loads(previous(PUBLIC[0]))["records"] if matches(row)))
    assert p490["post_adjudication_public_state"] == {
        "present_in_public_export": False, "map_record_count": 0, "canonical_and_historical_taxonomy_preserved": True}

    old_papers, old_maps = (json.loads(previous(path))["records"] for path in PUBLIC)
    delta = evidence["public_delta"]
    assert delta["removed_paper"] == next(row for row in old_papers if matches(row))
    assert delta["removed_relationships"] == [row for row in old_maps if matches(row)]
    assert {key: delta[key] for key in ("papers_removed", "relationships_removed", "unique_pairs_removed",
                                      "formal_removed", "mapped_removed")} == {
        "papers_removed": 1, "relationships_removed": 3, "unique_pairs_removed": 3,
        "formal_removed": 1, "mapped_removed": 1}
    assert delta["taxonomy_delta"] == {"detection": -1, "analysis_study": -1}
    assert delta["retained_paper_records_identical"] is delta["retained_relationship_records_identical"] is True
    assert delta["unrelated_institution_and_author_relationship_changes"] == 0
    context = load_context()
    assert evidence["corpus_before"] == original["corpus_counts"]
    assert evidence["corpus_after"] == evidence["corpus_counts"] == context["counts"] == CURRENT_CORPUS_COUNTS
    assert evidence["taxonomy_before"] == original["taxonomy_counts"]
    assert evidence["taxonomy_after"] == evidence["taxonomy_counts"] == CURRENT_TAXONOMY_TOTALS

    historical = [row for row in decision_rows(load_queues()) if row.get("batch") == "B"]
    decisions = read_review_decisions(ROOT / "data/curated/review_decisions.csv")
    resolved = {}
    for decision in decisions:
        match = re.search(r"\bBatch B review ([A-Z]\d{3});", decision["review_note"])
        if match and decision["action"] == "no_action_after_review":
            assert match.group(1) not in resolved
            resolved[match.group(1)] = decision["decision_id"]
    pending = [row for row in historical if row["review_id"] not in resolved]
    active = [row for row in pending if row["paper_id"] in context["papers"]]
    inactive = [row for row in pending if row["paper_id"] not in context["papers"]]
    account = evidence["accounting"]
    assert account["historical_actions"] == account["historical_review_records_retained"] == len(historical) == 159
    assert account["historical_papers"] == len({row["paper_id"] for row in historical}) == 148
    assert account["resolved_review_decision_ids"] == resolved
    assert account["resolved_review_ids"] == sorted(resolved)
    assert account["newly_resolved_bounded_questions"] == account["newly_completed_scope_decisions"] == 1
    assert account["historical_resolved_actions"] == len(resolved) == 6
    assert account["historical_unresolved_actions"] == len(pending) == 153
    assert account["active_public_unresolved_review_ids"] == [row["review_id"] for row in active]
    assert account["active_public_unresolved_actions"] == len(active) == 151
    assert account["active_public_unresolved_papers"] == len({row["paper_id"] for row in active}) == 140
    assert account["inactive_unresolved_review_ids"] == [row["review_id"] for row in inactive] == ["L015", "P562"]
    assert account["active_public_unresolved_by_prefix"] == dict(Counter(row["review_id"][0] for row in active))
    assert account["original_P490_short_name_question_pending"] is False
    assert account["independent_P526_venue_track_question_pending"] is account["T526_pending"] is True
    assert account["batch_c_deferred_cases"] == 13
