"""Bounded B1B adjudications preserve identities, independent reviews and history."""

from collections import Counter
import csv
from functools import lru_cache
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

import pytest

from scripts.curated_export import PaperIdentityCache, PaperIdentityIndex
from scripts.curated_schema import ALLOWED_REVIEW_ACTIONS, ALLOWED_REVIEW_QUEUES
from scripts.name_matching import canonical_name_key
from scripts.review_decisions import read_review_decisions
from scripts.validate_corpus_quality_audit import decision_rows, load_context, load_queues
from tests.baseline_expectations import CURRENT_CORPUS_COUNTS, CURRENT_TAXONOMY_TOTALS
from tests.corpus_quality_test_helpers import published_context

ROOT = Path(__file__).resolve().parents[1]
BASE = "1ea93c53a3d9f5f822ce27f818d8009274d3b12a"
B1B_ENDPOINT = "65e9422764c34eaad1d151fff2895e6c7503835f"
R137 = "curated:246f07c81b9f91e527eb"
R611 = "curated:07ee620b8169b67b900f"
L013 = "curated:9d04c60c5b0b70859a63"
FUDAN = "institution:baa1df7c4adddbda"
TITLE = "PatchCraft: Exploring Texture Patch for Efficient AI-Generated Image Detection"
P139 = "doi:10.1016/j.fsisyn.2026.100704"
P153 = "doi:10.1016/j.cosrev.2026.100908"
RESEARCH = {
    R137: ("method;dataset", "method;dataset;benchmark", "detection;source_attribution"),
    R611: ("method", "method;analysis_study", "source_attribution"),
}
SELECTED = {"R137": R137, "R611": R611, "L013": L013, "P139": P139, "P153": P153}
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
AFFILIATION_SOURCE = "data/processed/openalex_candidate_affiliations.csv"
# The operational input is ignored; verify its fixed evidence digest rather than stage it.
AFFILIATION_SOURCE_SHA256 = "edae6ebbf6b6c713b20fe66801724715fe58b5d0c9436bdd301902e63b10b1c9"


@lru_cache
def published(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


@lru_cache
def adjudicated(path):
    return subprocess.check_output(["git", "show", f"{B1B_ENDPOINT}:{path}"], cwd=ROOT)


def csvrows(raw):
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline="")))


def rows(path):
    return csvrows((ROOT / path).read_bytes())


def public(path, *, before=False):
    raw = published(path) if before else adjudicated(path)
    return json.loads(raw)["records"]


@lru_cache
def public_identity_index():
    # The canonical registry covers candidate records that do not export paper_id.
    return PaperIdentityIndex(rows("data/curated/paper_taxonomy.csv"), PaperIdentityCache())


def canonical_paper_id(record):
    matches = public_identity_index().matches(record)
    assert len(matches) == 1, record.get("title")
    return record.get("paper_id") or matches[0]["taxonomy_id"]


def ordered_public_identity(record, path):
    paper_id = canonical_paper_id(record)
    if path == PUBLIC[1]:
        # Preserve both relationship IDs and their paper/institution endpoints.
        assert record.get("id") and record.get("institution_id")
        return (paper_id, record["id"], record["institution_id"])
    return paper_id


@pytest.mark.parametrize("path", ["data/curated/papers.csv", "data/curated/paper_taxonomy.csv"])
def test_only_r137_and_r611_research_type_rows_change_with_original_csv_bytes_retained(path):
    old_bytes, new_bytes = published(path), adjudicated(path)
    before = {row["paper_id"]: row for row in csvrows(old_bytes)}
    after = {row["paper_id"]: row for row in csvrows(new_bytes)}
    assert before.keys() == after.keys()
    assert {pid for pid in before if before[pid] != after[pid]} == set(RESEARCH)
    for pid, (old_types, new_types, tasks) in RESEARCH.items():
        old, new = before[pid], after[pid]
        assert old["research_types"] == old_types
        assert new["research_types"] == new_types
        assert old["tasks"] == new["tasks"] == tasks
        allowed = {"research_types"}
        if path.endswith("paper_taxonomy.csv"):
            allowed |= {"research_types_status", "research_types_review_reason",
                        "research_types_evidence_tier", "research_types_evidence_source",
                        "research_types_evidence_excerpt", "audited_at"}
            assert new["research_types_status"] == "reviewed"
            assert new["research_types_evidence_tier"] == "primary_paper"
            assert all(new[field] for field in (
                "research_types_review_reason", "research_types_evidence_source",
                "research_types_evidence_excerpt", "audited_at"))
        changed = {field for field in old if old[field] != new[field]}
        assert "research_types" in changed and changed <= allowed
    old_lines, new_lines = old_bytes.splitlines(keepends=True), new_bytes.splitlines(keepends=True)
    assert len(old_lines) == len(new_lines)
    changes = [(old, new) for old, new in zip(old_lines, new_lines) if old != new]
    assert len(changes) == 2
    assert all(any(pid.encode() in old and pid.encode() in new for pid in RESEARCH)
               for old, new in changes)
    assert old_bytes.count(b"\r\n") == new_bytes.count(b"\r\n")


@pytest.mark.parametrize("path", PUBLIC)
def test_research_type_export_changes_retain_tasks_authors_and_all_other_metadata(path):
    before, after = public(path, before=True), public(path)
    for pid, (old_types, new_types, tasks) in RESEARCH.items():
        old_rows = [r for r in before if canonical_paper_id(r) == pid]
        new_rows = [r for r in after if canonical_paper_id(r) == pid]
        assert old_rows and len(old_rows) == len(new_rows)
        for old, new in zip(old_rows, new_rows):
            assert old["research_types"] == old_types.split(";")
            assert new["research_types"] == new_types.split(";")
            assert old["tasks"] == new["tasks"] == tasks.split(";")
            assert {k: v for k, v in old.items() if k not in {"research_types", "taxonomy_review"}} == {
                k: v for k, v in new.items() if k not in {"research_types", "taxonomy_review"}}
            assert {k: v for k, v in old["taxonomy_review"].items() if k != "research_types"} == {
                k: v for k, v in new["taxonomy_review"].items() if k != "research_types"}
            assert new["taxonomy_review"]["research_types"]["status"] == "reviewed"


def test_l013_roster_override_is_one_paper_specific_append_without_other_roster_edits():
    path = "data/curated/institution_author_overrides.csv"
    old, new = csvrows(published(path)), rows(path)
    assert new[:-1] == old and len(new) == len(old) + 1
    row = new[-1]
    assert row["title"] == TITLE and row["year"] == "2023"
    assert row["institution"] == "Fudan University"
    assert [name.strip() for name in row["authors"].split(";")] == [
        "Nan Zhong", "Yiran Xu", "Sheng Li", "Zhenxing Qian", "Xinpeng Zhang"]
    assert "L013" in row["notes"]
    assert canonical_name_key("Li, Sheng") == canonical_name_key("Sheng Li")
    assert list(new[-1]) == list(old[0])  # Existing roster schema; no identifier column invented.


def test_l013_source_author_identity_is_preserved_without_fabricating_a_missing_identifier():
    source = (ROOT / AFFILIATION_SOURCE).read_bytes()
    assert hashlib.sha256(source).hexdigest() == AFFILIATION_SOURCE_SHA256
    entries = [r for r in csvrows(source) if r["openalex_id"] == "https://openalex.org/W4388927818"]
    assert len(entries) == 5
    third = next(r for r in entries if r["author_order"] == "3")
    assert third["author_name"] == "Li, Sheng"
    assert third["author_openalex_id"] == ""  # Preserve missingness, rather than inventing an ID.
    assert [r["author_openalex_id"] for r in entries] == [
        "https://openalex.org/A5060167465", "https://openalex.org/A5101270212", "",
        "https://openalex.org/A5054324316", "https://openalex.org/A5101889360"]


def normalized_memberships(record):
    return [(canonical_name_key(a["author"]), tuple(a["indices"]), tuple(a["institution_ids"]))
            for a in record["author_affiliation_indices"]]


@pytest.mark.parametrize("path", PUBLIC)
def test_l013_roster_retains_person_order_fudan_links_and_relationship_identity(path):
    before = [r for r in public(path, before=True) if canonical_paper_id(r) == L013]
    after = [r for r in public(path) if canonical_paper_id(r) == L013]
    assert len(before) == len(after) == 1
    old, new = before[0], after[0]
    assert [a["name"] for a in old["authors"]] == [a["name"] for a in new["authors"]]
    assert len(new["authors"]) == 5
    assert normalized_memberships(new) == normalized_memberships(old)
    assert new["affiliations"] == old["affiliations"]
    assert all(a["institution_ids"] == [FUDAN] for a in new["author_affiliation_indices"])
    assert new["author_affiliation_counts"] == old["author_affiliation_counts"]
    expected = json.loads(json.dumps(old))
    for author in expected["authors"]:
        author["affiliation_source"] = "curated_admin"
    for item in expected["author_affiliation_indices"]:
        item["source"] = "curated_admin"
    for item in expected["author_institution_affiliations"]:
        item["authors"] = ["Sheng Li" if name == "Li, Sheng" else name for name in item["authors"]]
        item["mapping_source"] = "curated_admin"
    if "institution_authors" in expected:
        expected["institution_authors"] = ["Sheng Li" if name == "Li, Sheng" else name for name in expected["institution_authors"]]
    # The existing override appends a source note on the relationship, without certifying affiliations.
    assert {k: v for k, v in new.items() if k != "notes"} == {k: v for k, v in expected.items() if k != "notes"}
    if "notes" in new and new["notes"] != old.get("notes"):
        assert new["notes"].startswith(old.get("notes", ""))
        assert "manual institution-author override applied" in new["notes"] and "L013" in new["notes"]
    assert new["author_institution_affiliations"][0]["authors"] == [a["name"] for a in old["authors"]]
    if path == PUBLIC[1]:
        assert new["institution_authors"] == [a["name"] for a in old["authors"]]
        for key in ("id", "paper_id", "institution_id", "location_id", "latitude", "longitude",
                    "lat", "lon", "country", "country_code", "region", "city"):
            # Candidate relationships have no location_id. Preserve absent fields as absent.
            assert (key in new) == (key in old), key
            if key in old:
                assert new[key] == old[key], key
        assert new["id"] == "openalex-candidate-09d45f2a778956e5"
        assert new["institution_id"] == FUDAN


@pytest.mark.parametrize("path", PUBLIC)
def test_no_unrelated_public_paper_or_institution_changes_and_relationship_membership_stays_exact(path):
    old_payload, new_payload = json.loads(published(path)), json.loads(adjudicated(path))
    old, new = old_payload.pop("records"), new_payload.pop("records")
    assert [ordered_public_identity(r, path) for r in new] == [
        ordered_public_identity(r, path) for r in old]
    assert len(old) == len(new)
    assert [r for r in new if canonical_paper_id(r) not in set(SELECTED.values())] == [
        r for r in old if canonical_paper_id(r) not in set(SELECTED.values())]
    for payload in (old_payload, new_payload):
        payload["metadata"].pop("public_preview_generated_at", None)
    assert old_payload == new_payload


@pytest.mark.parametrize("pid,venue", [(P139, "Forensic Science International: Synergy"),
                                       (P153, "Computer Science Review")])
@pytest.mark.parametrize("path", PUBLIC)
def test_publication_no_change_decisions_preserve_bibliographic_history(path, pid, venue):
    old_rows = [r for r in public(path, before=True) if canonical_paper_id(r) == pid]
    new_rows = [r for r in public(path) if canonical_paper_id(r) == pid]
    assert len(old_rows) == len(new_rows) and old_rows
    diagnostics = {"venue_review_required", "venue_review_reason", "ambiguity_status", "metadata_status"}
    for old, new in zip(old_rows, new_rows):
        assert new["venue_name"] == old["venue_name"] == venue
        assert new["venue_acronym"] == old["venue_acronym"] == ""
        assert {k: v for k, v in new.items() if k not in diagnostics} == {
            k: v for k, v in old.items() if k not in diagnostics}
        assert old["venue_review_required"] is True and new["venue_review_required"] is False
        assert not new.get("venue_review_reason")
        # Resolution changes the venue review indicator only; all other status fields stay fixed.
        for status in (old["metadata_status"], new["metadata_status"]):
            assert status["overall"] == old["metadata_status"]["overall"]
        old_status = json.loads(json.dumps(old["metadata_status"]))
        new_status = json.loads(json.dumps(new["metadata_status"]))
        old_status["field_overrides"].pop("venue", None)
        new_status["field_overrides"].pop("venue", None)
        assert new_status == old_status
        assert new["metadata_status"]["field_overrides"].get("venue", {}).get("status") != "Needs review"


def test_exactly_five_existing_schema_decisions_append_with_bounded_review_identity():
    path = "data/curated/review_decisions.csv"
    before, after = csvrows(published(path)), csvrows(adjudicated(path))
    assert after[:len(before)] == before
    added = after[len(before):]
    assert len(added) == 5 and len({r["decision_id"] for r in added}) == 5
    originals = {r["review_id"]: r for r in decision_rows(load_queues()) if r.get("batch") == "B"}
    seen = set()
    for row in added:
        review_ids = set(re.findall(r"\b(?:R137|R611|L013|P139|P153)\b", row["review_note"]))
        assert len(review_ids) == 1
        rid = review_ids.pop()
        assert rid not in seen
        seen.add(rid)
        original = originals[rid]
        assert original["paper_id"] == SELECTED[rid] and original["title"] == row["title"]
        assert row["target_type"] == "paper"
        assert row["action"] == "no_action_after_review" in ALLOWED_REVIEW_ACTIONS
        assert row["review_queue"] in ALLOWED_REVIEW_QUEUES
        assert row["created_by"] == "maintainer-approved-batch-b-b1b"
        if rid.startswith("P"):
            assert row["review_queue"] == "publication_venues" and "[venue-state:" in row["review_note"]
            assert "SUPPORTED_NO_CHANGE" in row["review_note"]
        else:
            assert row["review_queue"] == "other" and "PROPOSE_CORRECTION_ACCEPTED" in row["review_note"]
    assert seen == SELECTED.keys()


def test_batch_b_original_questions_preserved_and_only_five_public_questions_resolve():
    audit = "data/raw/corpus_quality_audit_2026_10_04/"
    for filename in ("unmapped_papers.json", "taxonomy_review.json", "relationship_review.json", "publication_metadata_review.json"):
        path = audit + filename
        assert (ROOT / path).read_bytes() == published(path)
    historical = [r for r in decision_rows(load_queues()) if r.get("batch") == "B"]
    assert len(historical) == 159 and len({r["paper_id"] for r in historical}) == 148
    current_public = set(b1b_context()["papers"])
    applicable = [r for r in historical if r["paper_id"] in current_public]
    # Derive the effective closure set from persisted terminal decisions, not
    # from an arithmetic assumption about the five selected papers.
    decision_path = "data/curated/review_decisions.csv"
    previous_count = len(csvrows(published(decision_path)))
    added = csvrows(adjudicated(decision_path))[previous_count:]
    resolved = set()
    for decision in added:
        assert decision["action"] == "no_action_after_review"
        match = re.search(r"\bBatch B review ([A-Z]\d{3})\b", decision["review_note"])
        assert match and decision["created_by"] == "maintainer-approved-batch-b-b1b"
        resolved.add(match.group(1))
    assert resolved == SELECTED.keys()
    unresolved = [r for r in applicable if r["review_id"] not in resolved]
    assert len(applicable) == 157 and len({r["paper_id"] for r in applicable}) == 146
    assert len(unresolved) == 152 and len({r["paper_id"] for r in unresolved}) == 141
    assert {r["review_id"] for r in historical if r["paper_id"] not in current_public} == {"L015", "P562"}
    # A same-paper question would remain pending unless its exact ID was independently selected.
    assert {r["review_id"] for r in unresolved} == {r["review_id"] for r in applicable} - SELECTED.keys()


def test_published_b1b_research_type_counts_recompute_with_exact_two_label_delta():
    context = b1b_context()
    assert context["counts"] == {"public": 636, "formal": 528, "mapped": 614, "unmapped": 22, "relationship_rows": 1413, "unique_paper_institution_pairs": 1413}
    current = Counter(label for p in context["papers"].values() for dimension in ("tasks", "research_types") for label in p[dimension])
    before = Counter(label for p in public(PUBLIC[0], before=True) for dimension in ("tasks", "research_types") for label in p[dimension])
    assert current == {"detection": 586, "source_attribution": 84, "localization": 43, "method": 545, "dataset": 132, "benchmark": 89, "survey": 20, "analysis_study": 78}
    assert current - before == {"benchmark": 1, "analysis_study": 1}
    assert not before - current


@pytest.mark.parametrize("path", [
    "data/raw/corpus_quality_batch_b_wave_b1a_2026_10_12/evidence_manifest.json",
    "docs/corpus_quality_batch_b_wave_b1a_2026_10_12.md",
    "data/raw/corpus_quality_batch_c_closeout_2026_10_11/evidence_manifest.json",
    "docs/corpus_quality_batch_c_closeout_2026_10_11.md",
    "data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json",
])
def test_published_scope_and_deferred_evidence_receipts_remain_frozen(path):
    assert (ROOT / path).read_bytes() == published(path)


def test_all_frozen_neurips_artifacts_remain_byte_identical():
    receipt = json.loads((ROOT / "data/raw/systematic_gap_migration_2026_10_03/baseline.json").read_text())
    frozen = receipt["frozen_sha256"]
    assert len(frozen) == 49
    for path, expected in frozen.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path


@pytest.mark.parametrize("path", [
    "data/curated/author_institution_mappings.csv",
    "data/curated/institutions.csv",
    "data/curated/institution_locations.csv",
    "data/curated/institution_hierarchy.csv",
    "data/curated/institution_aliases.csv",
    "data/curated/paper_exclusions.csv",
    "data/manual/key_paper_affiliation_enrichment.csv",
])
def test_unrelated_author_institution_and_scope_sources_remain_exact(path):
    assert adjudicated(path) == published(path)
    if path != "data/curated/paper_exclusions.csv":
        assert (ROOT / path).read_bytes() == adjudicated(path)


MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1b_2026_10_15/evidence_manifest.json"
ORIGINAL_EVIDENCE_HASHES = {
    "manifest": "68f4e0a44a071c9031de311b904d73674b16a2154a0ceed15b20a054910d0d11",
    "report": "513cc4216699b4e252a66c15c760a29fff3f905f483dc70968c48652ea97b532",
}


def adjudication_manifest():
    return json.loads((ROOT / MANIFEST).read_text())


def original_evidence_manifest(packet):
    import base64
    import gzip

    originals = {}
    for key, expected in ORIGINAL_EVIDENCE_HASHES.items():
        archive = packet["evidence_only_archives"][key]
        compressed = base64.b64decode(archive["payload"], validate=True)
        assert archive["encoding"] == "gzip+base64"
        assert hashlib.sha256(compressed).hexdigest() == archive["compressed_sha256"]
        raw = gzip.decompress(compressed)
        assert len(raw) == archive["bytes"]
        assert hashlib.sha256(raw).hexdigest() == archive["sha256"] == expected
        originals[key] = raw
    return json.loads(originals["manifest"])


def test_manifest_binds_five_accepted_outcomes_to_persisted_decisions_and_preserved_evidence():
    packet = adjudication_manifest()
    original = original_evidence_manifest(packet)
    before = {row["review_id"]: row for row in original["records"]}
    after = {row["review_id"]: row for row in packet["records"]}
    assert len(packet["records"]) == len(after) == 5
    assert before.keys() == after.keys() == SELECTED.keys()
    assert packet["baseline"]["commit"] == BASE
    decisions = {row["decision_id"]: row for row in read_review_decisions(ROOT / "data/curated/review_decisions.csv")}
    for review_id, record in after.items():
        preserved = before[review_id]
        assert record["canonical_identity"] == preserved["canonical_identity"]
        assert record["canonical_identity"]["paper_id"] == SELECTED[review_id]
        for key in ("original_review", "exact_original_review_question", "question_assessed", "locked_policies", "confidence"):
            assert record[key] == preserved[key]
        assert record["evidence_only_review"] == preserved["evidence_review"]
        assert record["maintainer_accepted"] is True
        assert record["maintainer_acceptance_pending"] is False
        assert record["formal_review_action_closed"] is True
        correction = review_id in {"R137", "R611", "L013"}
        assert record["final_disposition"] == ("PROPOSE_CORRECTION_ACCEPTED" if correction else "SUPPORTED_NO_CHANGE")
        assert record["remediation_required"] is correction
        assert record["remediation_applied"] is correction
        decision = record["review_decision"]
        assert decisions[decision["decision_id"]] == decision
        assert f"Batch B review {review_id};" in decision["review_note"]
        current = b1b_context()["papers"][SELECTED[review_id]]
        assert record["post_adjudication_public_state"] == {
            key: current.get(key) for key in record["post_adjudication_public_state"]}
    assert packet["scope"]["selected_review_ids"] == list(SELECTED)
    assert packet["scope"]["authoritative_corrections_applied"] == 3
    assert packet["scope"]["no_change_resolutions"] == 2
    assert packet["scope"]["scientific_network_requests"] == packet["scope"]["new_manuscripts_retrieved"] == 0
    assert packet["summary"]["formal_review_actions_closed"] == 5
    assert packet["summary"]["maintainer_acceptances_pending"] == 0


def test_manifest_accounting_and_taxonomy_reconcile_actual_records_and_decisions():
    packet = adjudication_manifest()
    context = b1b_context()
    original = [row for row in decision_rows(load_queues()) if row.get("batch") == "B"]
    resolved = set(packet["accounting"]["resolved_review_ids"])
    decision_ids = {record["review_id"]: record["review_decision"]["decision_id"] for record in packet["records"]}
    assert resolved == SELECTED.keys()
    assert packet["accounting"]["resolved_review_decision_ids"] == decision_ids
    pending = [row for row in original if row["paper_id"] in context["papers"] and row["review_id"] not in resolved]
    account = packet["accounting"]
    assert account["historical_actions"] == account["historical_review_records_retained"] == len(original) == 159
    assert account["historical_unique_papers"] == len({r["paper_id"] for r in original}) == 148
    assert account["wave_questions_resolved"] == len(resolved) == 5
    assert account["active_public_unresolved_review_ids"] == [r["review_id"] for r in pending]
    assert account["active_public_unresolved_actions"] == len(pending) == 152
    assert account["active_public_unique_papers_with_unresolved_actions"] == len({r["paper_id"] for r in pending}) == 141
    assert account["active_public_unresolved_by_prefix"] == dict(Counter(r["review_id"][0] for r in pending))
    assert account["inactive_unresolved_review_ids"] == ["L015", "P562"]
    assert account["batch_c_external_debts_deferred"] == 13
    assert packet["corpus_before"] == packet["corpus_after"] == context["counts"]
    before = Counter(label for paper in public(PUBLIC[0], before=True) for dim in ("tasks", "research_types") for label in paper[dim])
    after = Counter(label for paper in context["papers"].values() for dim in ("tasks", "research_types") for label in paper[dim])
    assert packet["taxonomy_before"] == dict(before)
    assert packet["taxonomy_after"] == dict(after)
    assert after - before == {"benchmark": 1, "analysis_study": 1} and not before - after


def test_manifest_preserves_original_source_provenance_and_current_source_hashes():
    packet = adjudication_manifest()
    original = original_evidence_manifest(packet)
    source_hashes = {entry["path"]: entry["sha256"] for entry in original["source_files"]}
    assert len(source_hashes) == 31
    assert packet["evidence_only_source_files"] == original["source_files"]
    assert packet["evidence_only_source_sha256"] == source_hashes
    assert packet["current_source_sha256"].keys() == source_hashes.keys()
    for path, expected in packet["current_source_sha256"].items():
        snapshot = ((ROOT / path).read_bytes() if path == "data/raw/openalex/20260619T211726Z_001_ai-generated-image-detection.json" else adjudicated(path))
        assert hashlib.sha256(snapshot).hexdigest() == expected, path
    for path, expected in packet["core_unchanged_sha256"].items():
        assert hashlib.sha256(adjudicated(path)).hexdigest() == expected, path
        assert hashlib.sha256(published(path)).hexdigest() == expected, path


@lru_cache
def b1b_context():
    """Recompute the immutable B1B transaction independently of later decisions."""
    return published_context(B1B_ENDPOINT)


def test_live_b1b_adjudications_survive_successor_scope_decisions():
    current = load_context()
    assert current["counts"] == CURRENT_CORPUS_COUNTS
    totals = Counter(label for paper in current["papers"].values()
                     for dimension in ("tasks", "research_types") for label in paper[dimension])
    assert totals == CURRENT_TAXONOMY_TOTALS
    # Keep accepted canonical rows strict in the live registry while the whole
    # original transaction is evaluated at its immutable published endpoint.
    for path, key in (("data/curated/papers.csv", "paper_id"),
                      ("data/curated/paper_taxonomy.csv", "taxonomy_id")):
        historical = {row[key]: row for row in csvrows(adjudicated(path))}
        live = {row[key]: row for row in rows(path)}
        for pid in RESEARCH:
            target = pid if key == "paper_id" else "paper_id:" + pid
            assert live[target] == historical[target]
    for path in PUBLIC:
        current_records = json.loads((ROOT / path).read_bytes())["records"]
        assert [row for row in current_records if canonical_paper_id(row) in SELECTED.values()] == [
            row for row in public(path) if canonical_paper_id(row) in SELECTED.values()]
    published_decisions = csvrows(adjudicated("data/curated/review_decisions.csv"))
    live_decisions = read_review_decisions(ROOT / "data/curated/review_decisions.csv")
    assert live_decisions[:len(published_decisions)] == published_decisions
    b1b_ids = {row["decision_id"] for row in published_decisions
               if row["created_by"] == "maintainer-approved-batch-b-b1b"}
    assert len(b1b_ids) == 5
    assert all(sum(row["decision_id"] == decision_id for row in live_decisions) == 1
               for decision_id in b1b_ids)
