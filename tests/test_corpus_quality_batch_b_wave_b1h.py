"""R566's accepted research-type correction preserves R267 and prior evidence."""
from collections import Counter
from copy import deepcopy
import base64
import csv
from datetime import datetime, timezone
from functools import lru_cache
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

import pytest

from scripts.curated_schema import ALLOWED_REVIEW_ACTIONS, ALLOWED_REVIEW_QUEUES
from scripts.literature51_reproducibility import preserved_bytes
from scripts.review_decisions import read_review_decisions, upsert_review_decision
from scripts.validate_corpus_quality_audit import decision_rows, load_context, load_queues
from tests.corpus_quality_test_helpers import csv_records, published_bytes, published_context
from tests.baseline_expectations import CURRENT_CORPUS_COUNTS, CURRENT_TAXONOMY_TOTALS

ROOT = Path(__file__).resolve().parents[1]
BASE = "445b4f8cc7257b3c87868a666bce43d8c20bda0d"
# Whole-file and transaction receipts describe the immutable published B1H endpoint.
PUBLISHED = "bb4b60b2ee612331b997d7482edaa1e9e657cff2"
PAPERS = "data/curated/papers.csv"
TAXONOMY = "data/curated/paper_taxonomy.csv"
DECISIONS = "data/curated/review_decisions.csv"
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1h_2026_10_19/evidence_manifest.json"
REPORT = "docs/corpus_quality_batch_b_wave_b1h_2026_10_19.md"
AUDIT = "data/raw/corpus_quality_audit_2026_10_04/"
FIXTURES = "tests/fixtures/historical_test_fixture_manifest.json"
R566 = "curated:67d37f98e44fa9d7d06e"
R267 = "curated:7693a9c0107feaf90e10"
DECISION_ID = "review:7ab9cfc3833aad630f20"
PDF_URL = ("https://openaccess.thecvf.com/content/CVPR2023W/WMF/papers/"
           "Corvi_Intriguing_Properties_of_Synthetic_Images_From_Generative_Adversarial_"
           "Networks_to_CVPRW_2023_paper.pdf")
PDF_SHA256 = "5b22d59439f359102c3a73d35018aa1b022704ba41ef83dc521d9dae86d32b6f"
EVIDENCE_HASHES = {
    "manifest": "dcc01300ffeb5e89df0dedc55ff461cbf441de836f3c8f4fcc65a9ed5b74937a",
    "report": "267495f79f287638f9313a216e18c2457377a49994a98f0f75a40dc408bc91a3",
}
CORPUS = {"public": 674, "formal": 557, "mapped": 613, "unmapped": 61,
          "relationship_rows": 1410, "unique_paper_institution_pairs": 1410}
TAXONOMY_TOTALS = {"detection": 621, "source_attribution": 84, "localization": 45,
                   "method": 578, "dataset": 134, "benchmark": 90, "survey": 21,
                   "analysis_study": 82}
REASON = (
    "R566 accepted under R3/R4: the complete official CVF CVPR Workshops 2023 accepted "
    "manuscript establishes primary systematic forensic analysis using established "
    "measurements, without an independently validated substantive novel algorithm. "
    "Replace method with analysis_study; preserve detection. IEEE-final/arXiv equivalence "
    "remains unverified."
)
EXCERPT = (
    "Section 4/Table 1: 15 model entries and source-statistics averages over 1000 images "
    "using an existing denoiser. Figure 3: upsampling 4/8 and spectral spacing 1/4/1/8; "
    "Figure 4: resize 2.0/1.4/0.7 and JPEG 99/95/75; Figures 6-7: 128 radial steps, "
    "16 angular steps, cutoff 0.1. These are measurement settings, not detector scores. "
    "Section 5 places detector design in future work. Reviewed CVF accepted version only; "
    "IEEE-final/arXiv equivalence unverified."
)
CSV_UPDATES = {
    PAPERS: {"research_types": "analysis_study"},
    TAXONOMY: {
        "research_types": "analysis_study",
        "research_types_review_reason": REASON,
        "research_types_evidence_tier": "primary_paper",
        "research_types_evidence_source": PDF_URL,
        "research_types_evidence_excerpt": EXCERPT,
        "audited_at": "2026-10-19",
    },
}
CSV_AFTER_HASHES = {
    PAPERS: "7d1994e5291a846546a037842d1fc72eb1b175339cf30a11fdf5cbc5f1859f7d",
    TAXONOMY: "f52659f8535106f2c2287bcf7e136e57766b81b34054b5012ac964ba67787e03",
}
MAP_IDS = {"curated-map:d59341f6b19cbc2f295e", "curated-map:7b90f0eba4b0f08f82c3"}
C13_FILES = (
    "data/raw/corpus_quality_batch_c_closeout_2026_10_11/evidence_manifest.json",
    "docs/corpus_quality_batch_c_closeout_2026_10_11.md",
    "docs/corpus_quality_batch_c_evidence_debt_triage_2026_10_08.md",
    "tests/test_corpus_quality_batch_c_closeout.py",
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


@lru_cache
def packet():
    return json.loads((ROOT / MANIFEST).read_bytes())


@lru_cache
def archived_bytes(kind):
    archive = packet()["evidence_only_packet_archives"][kind]
    assert archive["encoding"] == "gzip+base64"
    raw = gzip.decompress(base64.b64decode(archive["gzip_base64"], validate=True))
    assert len(raw) == archive["bytes"]
    assert digest(raw) == archive["sha256"] == EVIDENCE_HASHES[kind]
    return raw


@lru_cache
def original():
    return json.loads(archived_bytes("manifest"))


def record(data, review_id):
    matches = [row for row in data["records"] if row["review_id"] == review_id]
    assert len(matches) == 1
    return matches[0]


def selected_row(raw, paper_id):
    matches = [row for row in csv_records(raw) if row["paper_id"] == paper_id]
    assert len(matches) == 1
    return matches[0]


def terminal(decisions):
    result = {}
    for row in decisions:
        match = re.search(r"\bBatch B review ([A-Z]\d{3});", row["review_note"])
        if match and row["action"] == "no_action_after_review":
            assert match[1] not in result, "Original review has duplicate terminal decisions"
            result[match[1]] = row["decision_id"]
    return result


@lru_cache
def baseline_paths(*prefixes):
    return subprocess.check_output(
        ["git", "--no-optional-locks", "ls-tree", "-r", "--name-only", BASE,
         "--", *prefixes], cwd=ROOT, text=True).splitlines()


def logical_csv_chunks(raw):
    """Preserve logical-record bytes, including quoted embedded CRLF."""
    lines = raw.splitlines(keepends=True)
    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    chunks, start = [], 0
    for _ in reader:
        chunks.append(b"".join(lines[start:reader.line_num]))
        start = reader.line_num
    assert start == len(lines)
    return chunks


def replace_csv_tokens(raw, header, updates):
    """Build the expected target record without reserializing its other cells."""
    spans, start, index, quoted = [], 0, 0, False
    while index < len(raw):
        byte = raw[index]
        if byte == 34:
            if quoted and index + 1 < len(raw) and raw[index + 1] == 34:
                index += 2
                continue
            quoted = not quoted
        elif not quoted and byte == 44:
            spans.append((start, index))
            start = index + 1
        elif not quoted and byte in (10, 13):
            spans.append((start, index))
            break
        index += 1
    else:
        spans.append((start, len(raw)))
    assert not quoted and len(spans) == len(header)
    edits = []
    for field, value in updates.items():
        stream = io.StringIO(newline="")
        csv.writer(stream, lineterminator="\n").writerow([value])
        begin, end = spans[header.index(field)]
        edits.append((begin, end, stream.getvalue()[:-1].encode()))
    for begin, end, token in sorted(edits, reverse=True):
        raw = raw[:begin] + token + raw[end:]
    return raw


def accounting(decisions, public=None):
    ledger = [row for row in decision_rows(load_queues()) if row["batch"] == "B"]
    done = terminal(decisions)
    pending = [row for row in ledger if row["review_id"] not in done]
    public = load_context()["papers"] if public is None else public
    active = [row for row in pending if row["paper_id"] in public]
    return {
        "historical_actions": len(ledger),
        "historical_papers": len({row["paper_id"] for row in ledger}),
        "closed_review_ids": sorted(done),
        "historical_unresolved_actions": len(pending),
        "historical_unresolved_papers": len({row["paper_id"] for row in pending}),
        "active_public_unresolved_actions": len(active),
        "active_public_unresolved_papers": len({row["paper_id"] for row in active}),
        "historical_unresolved_review_ids": [row["review_id"] for row in pending],
        "active_public_unresolved_review_ids": [row["review_id"] for row in active],
    }


@pytest.mark.parametrize("kind", ["manifest", "report"])
def test_complete_evidence_only_packet_is_portably_archived_with_fixed_hashes(kind):
    assert archived_bytes(kind)
    assert set(packet()["evidence_only_packet_archives"]) == {"manifest", "report"}
    assert original()["validation"]["status"] == "PASS"
    assert original()["validation"]["lightweight_checks_passed"] == 68
    assert original()["validation"]["failures"] == 0


@pytest.mark.parametrize("path", [PAPERS, TAXONOMY])
def test_only_R566_changes_and_every_unapproved_CSV_token_retains_original_bytes(path):
    before_raw, after_raw = published_bytes(BASE, path), published_bytes(PUBLISHED, path)
    before, after = csv_records(before_raw), csv_records(after_raw)
    key = "taxonomy_id" if path == TAXONOMY else "paper_id"
    assert len(before) == len(after)
    assert [row[key] for row in after] == [row[key] for row in before]
    assert len({row[key] for row in before}) == len(before)
    assert {old["paper_id"] for old, new in zip(before, after) if old != new} == {R566}
    old_target, new_target = selected_row(before_raw, R566), selected_row(after_raw, R566)
    updates = CSV_UPDATES[path]
    assert {key for key in old_target if old_target[key] != new_target[key]} == updates.keys()
    assert new_target == {**old_target, **updates}
    assert new_target == packet()["adjudication"]["row_after"][path]
    assert new_target["tasks"] == "detection"
    assert new_target["image_scopes"] == "fully_generated"
    old_chunks, new_chunks = logical_csv_chunks(before_raw), logical_csv_chunks(after_raw)
    assert len(old_chunks) == len(new_chunks) == len(before) + 1
    header = next(csv.reader(io.StringIO(before_raw.decode(), newline="")))
    expected = [old_chunks[0]]
    for old, old_chunk in zip(before, old_chunks[1:]):
        expected.append(replace_csv_tokens(old_chunk, header, updates)
                        if old["paper_id"] == R566 else old_chunk)
    assert after_raw == b"".join(expected)
    assert digest(after_raw) == CSV_AFTER_HASHES[path]
    # Later approved records may change; this accepted target must remain exact.
    assert selected_row((ROOT / path).read_bytes(), R566) == new_target
    changes = packet()["adjudication"]["csv_changes"]
    change = next(row for row in changes if row["path"] == path)
    assert change["row_identity"] == {"paper_id": R566}
    assert change["changed_fieldnames"] == list(updates)
    assert change["before_fields"] == {key: old_target[key] for key in updates}
    assert change["after_fields"] == updates
    assert change["before_sha256"] == digest(before_raw)
    assert change["planned_after_sha256"] == digest(after_raw)


def test_exactly_one_schema_supported_R566_terminal_append_preserves_prior_bytes():
    before, after = published_bytes(BASE, DECISIONS), published_bytes(PUBLISHED, DECISIONS)
    assert after.startswith(before)
    old, rows = csv_records(before), csv_records(after)
    assert len(old) == 86 and len(rows) == 87
    assert rows[:-1] == old
    assert len({row["decision_id"] for row in rows}) == len(rows)
    assert terminal(rows) == {**terminal(old), "R566": DECISION_ID}
    row = rows[-1]
    assert row["decision_id"] == DECISION_ID
    assert row["review_queue"] == "other" and row["review_queue"] in ALLOWED_REVIEW_QUEUES
    assert row["action"] == "no_action_after_review" and row["action"] in ALLOWED_REVIEW_ACTIONS
    assert row["target_type"] == "paper" and row["institution"] == ""
    assert row["year"] == "2023" and row["doi"] == "10.1109/cvprw59228.2023.00104"
    assert row["openalex_url"] == "https://openalex.org/W4385815563"
    assert row["title"] == selected_row(published_bytes(BASE, PAPERS), R566)["title"]
    assert row["created_by"] == "maintainer-approved-batch-b-b1h"
    assert row["created_at"] == row["updated_at"]
    assert row["created_at"].startswith("2026-10-20T")
    timestamp = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
    assert timestamp.tzinfo == timezone.utc
    identity = "|".join(" ".join(row[key].split()).casefold() for key in
                        ("review_queue", "target_type", "doi", "openalex_url", "title", "year", "institution"))
    assert "review:" + digest(identity.encode())[:20] == DECISION_ID
    for token in ("Batch B review R566;", "PROPOSE_CORRECTION_ACCEPTED",
                  "method -> analysis_study", "1000", "15", "128", "16", "0.1",
                  "future work", "IEEE-final", "arXiv", "unverified", PDF_URL, PDF_SHA256):
        assert token in row["review_note"]
    adjudication = packet()["adjudication"]
    assert adjudication["decision_id"] == DECISION_ID
    assert adjudication["terminal_decision"] == row
    assert adjudication["before_registry_sha256"] == digest(before)
    assert adjudication["after_registry_sha256"] == digest(after)
    assert len(adjudication["csv_changes"]) == 2
    live_raw = (ROOT / DECISIONS).read_bytes()
    live_rows = read_review_decisions(ROOT / DECISIONS)
    assert live_raw.startswith(after)
    assert [candidate for candidate in live_rows if candidate["decision_id"] == DECISION_ID] == [row]
    assert terminal(live_rows)["R566"] == DECISION_ID


def test_R566_decision_upsert_is_idempotent_without_timestamp_or_byte_churn(tmp_path):
    path = tmp_path / "review_decisions.csv"
    before = (ROOT / DECISIONS).read_bytes()
    path.write_bytes(before)
    row = next(row for row in read_review_decisions(path) if row["decision_id"] == DECISION_ID)
    assert upsert_review_decision(row, path=path) == row
    assert path.read_bytes() == before


def test_R267_is_unchanged_at_the_immutable_B1H_endpoint_and_live_task_metadata_is_preserved():
    for path in (PAPERS, TAXONOMY):
        old = selected_row(published_bytes(BASE, path), R267)
        current = selected_row(published_bytes(PUBLISHED, path), R267)
        assert current == old
        assert current["research_types"] == "method" and current["tasks"] == "detection"
    public = published_context(PUBLISHED)["papers"][R267]
    assert public == published_context(BASE)["papers"][R267]
    assert public["research_types"] == ["method"] and public["tasks"] == ["detection"]
    assert "Yao_Xiao" in selected_row(published_bytes(PUBLISHED, PAPERS), R267)["authors"]
    assert "R267" not in terminal(csv_records(published_bytes(PUBLISHED, DECISIONS)))

    # R267's later accepted B1O role addition must not rewrite B1H history or tasks.
    for path in (PAPERS, TAXONOMY):
        old = selected_row(published_bytes(PUBLISHED, path), R267)
        live = selected_row((ROOT / path).read_bytes(), R267)
        mutable = {"research_types"} if path == PAPERS else {
            "research_types", "research_types_review_reason", "research_types_evidence_tier",
            "research_types_evidence_source", "research_types_evidence_excerpt", "audited_at"}
        assert {key: value for key, value in old.items() if key not in mutable} == {
            key: value for key, value in live.items() if key not in mutable}


def test_public_delta_is_one_paper_and_two_map_research_type_metadata_changes_only():
    old_context, current = published_context(BASE), published_context(PUBLISHED)
    assert current["papers"].keys() == old_context["papers"].keys()
    assert {pid for pid in current["papers"]
            if current["papers"][pid] != old_context["papers"][pid]} == {R566}
    assert sum(current["papers"][pid] == old_context["papers"][pid]
               for pid in current["papers"] if pid != R566) == 673
    expected = deepcopy(old_context["papers"][R566])
    expected["research_types"] = ["analysis_study"]
    expected["taxonomy_review"]["research_types"]["reason"] = REASON
    assert current["papers"][R566] == expected
    assert current["pairs"] == old_context["pairs"]
    for path in PUBLIC:
        old_payload = json.loads(published_bytes(BASE, path))
        payload = json.loads(published_bytes(PUBLISHED, path))
        old_metadata, metadata = deepcopy(old_payload["metadata"]), deepcopy(payload["metadata"])
        old_metadata.pop("public_preview_generated_at", None)
        metadata.pop("public_preview_generated_at", None)
        assert metadata == old_metadata
        assert {key: value for key, value in payload.items() if key not in {"records", "metadata"}} == {
            key: value for key, value in old_payload.items() if key not in {"records", "metadata"}}
    old_maps = {row["id"]: row for row in json.loads(published_bytes(BASE, PUBLIC[1]))["records"]}
    new_maps = {row["id"]: row for row in json.loads(published_bytes(PUBLISHED, PUBLIC[1]))["records"]}
    assert len(old_maps) == len(new_maps) == 1410 and old_maps.keys() == new_maps.keys()
    assert {key for key in old_maps if old_maps[key] != new_maps[key]} == MAP_IDS
    for key, old in old_maps.items():
        expected = deepcopy(old)
        if key in MAP_IDS:
            assert old["paper_id"] == R566
            expected["research_types"] = ["analysis_study"]
            expected["taxonomy_review"]["research_types"]["reason"] = REASON
        assert new_maps[key] == expected, key
        assert (new_maps[key]["id"], new_maps[key]["institution_id"]) == (
            old["id"], old["institution_id"])
    live = load_context()
    assert live["papers"][R566] == current["papers"][R566]
    assert live["pairs"] == current["pairs"]
    live_maps = {row["id"]: row for row in json.loads((ROOT / PUBLIC[1]).read_bytes())["records"]}
    assert {key: live_maps[key] for key in MAP_IDS} == {key: new_maps[key] for key in MAP_IDS}


def test_corpus_and_taxonomy_totals_recompute_the_exact_single_paper_transfer():
    old, current = published_context(BASE), published_context(PUBLISHED)
    assert current["counts"] == old["counts"] == packet()["corpus_counts"] == CORPUS
    def counts(papers):
        return Counter(label for paper in papers.values() for dimension in ("tasks", "research_types")
                       for label in paper[dimension])
    before, after = counts(old["papers"]), counts(current["papers"])
    assert after == packet()["taxonomy_counts"] == TAXONOMY_TOTALS
    assert {key: after[key] - before[key] for key in before if after[key] != before[key]} == {
        "method": -1, "analysis_study": 1}
    assert R566 not in {pid for pid, paper in current["papers"].items() if "method" in paper["research_types"]}
    assert R566 in {pid for pid, paper in current["papers"].items() if "analysis_study" in paper["research_types"]}
    assert current["papers"][R566]["tasks"] == ["detection"]
    live = load_context()
    assert live["counts"] == CURRENT_CORPUS_COUNTS
    assert counts(live["papers"]) == CURRENT_TAXONOMY_TOTALS
    assert live["papers"][R566] == current["papers"][R566]


def test_original_whole_scientific_records_and_source_provenance_remain_lossless():
    old, new = original(), packet()
    assert [row["review_id"] for row in new["records"]] == ["R267", "R566"]
    assert record(new, "R267") == record(old, "R267")
    prior, accepted = record(old, "R566"), record(new, "R566")
    changed_flags = {"maintainer_acceptance_pending", "review_closed",
                     "terminal_review_decision_created", "authoritative_changes_applied"}
    assert set(accepted) == set(prior) | {"accepted_outcome", "terminal_review_decision_id",
                                          "adjudication", "final_authoritative_taxonomy"}
    for key in prior:
        if key not in changed_flags:
            assert accepted[key] == prior[key], key
    assert accepted["scientific_evidence"] == prior["scientific_evidence"]
    assert accepted["maintainer_acceptance_pending"] is False
    assert accepted["review_closed"] is True
    assert accepted["terminal_review_decision_created"] is True
    assert accepted["authoritative_changes_applied"] is True
    assert accepted["accepted_outcome"] == "PROPOSE_CORRECTION_ACCEPTED"
    assert accepted["terminal_review_decision_id"] == DECISION_ID
    assert accepted["final_authoritative_taxonomy"] == {
        "tasks": ["detection"], "image_scopes": ["fully_generated"],
        "research_types": ["analysis_study"],
    }
    assert accepted["adjudication"] == new["adjudication"]
    assert new["adjudication"]["retained_tasks"] == ["detection"]
    assert new["adjudication"]["final_research_types"] == ["analysis_study"]
    for key in ("retrieval_accounting", "locked_policies", "independent_root_review",
                "source_files_sha256", "operational_review_sha256", "preservation",
                "separate_import_review_inventory", "batch_c_deferred_accounting"):
        assert new[key] == old[key], key
    for key in ("scope", "validation", "integrity", "corpus_counts", "taxonomy_counts",
                "batch_b_accounting", "accounting_effect", "final_git_requirements"):
        assert new["evidence_only_" + key] == old[key], key


def test_R566_reviewed_CVF_accepted_version_and_analysis_method_boundary_are_explicit():
    evidence = record(packet(), "R566")["scientific_evidence"]
    source = evidence["source_provenance"]
    pdf = source["official_pdf"]
    assert pdf["url"] == PDF_URL and pdf["sha256"] == PDF_SHA256
    assert pdf["bytes"] == 2097562 and pdf["pdf_pages"] == 10
    assert pdf["printed_pages"] == "973-982"
    assert pdf["identity_match_title_and_all_five_authors"] is True
    assert pdf["complete_verified"] is True and pdf["eof_verified"] is True
    assert evidence["coverage"]["pages_read_completely"] == list(range(1, 11))
    assert "accepted-version" in source["version_boundary"]
    assert "IEEE" in source["version_boundary"] and "arXiv" in source["version_boundary"]
    assert "workshop" in source["metadata_discrepancy_not_corrected"].casefold()
    assert evidence["analysis_study_assessment"]["supported"] is True
    method = evidence["method_specific_assessment"]
    assert method["substantive_new_method_supported"] is False
    assert "future work" in method["strong_positive_boundary"]["quote"]
    assert "technical analytical work" in method["contrary_evidence_considered"]
    assert evidence["policy_application"]["R3"]["decision"] == "analysis_study supported"
    assert evidence["policy_application"]["R4"]["decision"] == "method not independently supported"
    assert evidence["proposed_final_research_types"] == ["analysis_study"]
    assert evidence["method_should_be_retained"] is False


def test_R566_quantitative_settings_and_confounders_are_not_promoted_to_detector_scores():
    evidence = record(packet(), "R566")["scientific_evidence"]
    assert evidence["model_inventory"]["table_model_rows"] == 15
    assert len(evidence["model_inventory"]["rows"]) == 15
    findings = {row["id"]: row for row in evidence["structured_quantitative_findings"]}
    assert findings["F2"]["exact_parameters"]["upsampling_factors"] == [4, 4, 8]
    assert findings["F2"]["exact_parameters"]["spectral_peak_spacing_cycles_per_pixel"] == [0.25, 0.25, 0.125]
    assert "not an isolated controlled causal" in findings["F2"]["causal_limit"]
    assert findings["F3"]["exact_parameters"]["resizing_scales"] == [2.0, 1.4, 0.7]
    assert findings["F3"]["exact_parameters"]["JPEG_quality_factors"] == [99, 95, 75]
    assert findings["F5"]["exact_parameters"]["source_images"] == 1000
    assert findings["F5"]["exact_parameters"]["radial_samples"] == 128
    assert findings["F6"]["exact_parameters"]["angular_samples"] == 16
    assert findings["F6"]["exact_parameters"]["high_pass_cutoff_frequency"] == 0.1
    assert "not an independently evaluated per-image classifier" in findings["F6"]["metric_boundary"]
    assert "not performance evaluation" in evidence["method_specific_assessment"]["independent_quantitative_method_evaluation"]
    issues = {row["issue"]: row for row in evidence["contradictions_and_limitations"]}
    assert {"Source matching is incompletely documented", "Architecture and dataset confounding",
            "Preprocessing can overwhelm source traces", "FFHQ exception and source preprocessing",
            "No inference from descriptive plots to detector performance", "Version/publication metadata"} <= issues.keys()
    assert "Unknown" in issues["Source matching is incompletely documented"]["finding"]


def test_R267_all_fourteen_questions_and_ordered_access_failures_remain_unverified():
    case = record(packet(), "R267")
    assert case == record(original(), "R267")
    assert case["provisional_outcome"] == "EVIDENCE_STILL_INSUFFICIENT"
    assert case["proposed_research_types"] is None
    assert case["administrative_retained_research_types"] == ["method"]
    assert case["maintainer_acceptance_pending"] is True
    assert case["review_closed"] is False and case["terminal_review_decision_created"] is False
    assert case["authoritative_changes_applied"] is False
    evidence = case["scientific_evidence"]
    assert len(evidence["scientific_checks"]) == 14
    assert {row["status"] for row in evidence["scientific_checks"]} == {"UNVERIFIED"}
    assert evidence["exact_quantitative_evidence"]["scientific_result_values"] == []
    assert evidence["exact_quantitative_evidence"]["structured_numeric_tables"] == []
    provenance = evidence["manuscript_provenance"]
    assert provenance["complete_manuscript_obtained"] is False
    assert provenance["complete_manuscript_sha256"] is None
    assert provenance["pages_read"] == provenance["pages_rendered"] == []
    assert evidence["primary_identity_metadata"]["bibliographic_span_inclusive_pages"] == 22
    assert len(evidence["primary_identity_metadata"]["ordered_official_authors"]) == 10
    assert "zero manuscript pages" in evidence["primary_identity_metadata"]["bibliographic_span_boundary"]
    retrieval = evidence["retrieval_accounting"]
    assert retrieval["complete_unique_manuscripts"] == 0
    assert retrieval["requests_stopped_after_final_fallback"] is True
    attempts = retrieval["all_attempts"]
    assert [row["attempt"] for row in attempts] == [1, 2, 3, 4, 5]
    assert all(row["complete_manuscript"] is False for row in attempts)
    assert attempts[0]["http_status"] == 0 and attempts[0]["received_bytes"] == 0
    assert attempts[1]["http_status"] == 200 and attempts[1]["exit_code"] == 28
    assert attempts[1]["received_bytes"] == 10759 and attempts[1]["declared_content_length"] == 13757845
    assert attempts[1]["has_pdf_eof"] is False
    assert "400" in attempts[2]["result"] and "octet-stream" in attempts[2]["result"]
    assert attempts[3]["http_status"] == 404 and "HEAD" in attempts[3]["kind"]
    assert attempts[4]["final_url"] == "https://openreview.net/challenge?redirect=/pdf?id%3DsKYdVKE1tS"
    assert "not a PDF" in attempts[4]["result"]
    assert provenance["partial_pdf"]["sha256"] == "4ad66065c072261994deb0437b0266b47de8967fd626052138c66cc4d19e8c1d"
    assert provenance["partial_pdf"]["not_scientific_evidence"] is True


def test_one_R566_manuscript_is_not_counted_as_two_HTTP_responses_or_R267_success():
    retrieval = packet()["retrieval_accounting"]
    assert retrieval == original()["retrieval_accounting"]
    assert retrieval["successful_full_manuscripts_by_review"] == {"R267": 0, "R566": 1}
    assert retrieval["successful_full_manuscripts_total"] == 1
    assert retrieval["transport_attempts_by_review"] == {"R267": 5, "R566": 2}
    assert retrieval["complete_bytes_sha256"] == {"R566": PDF_SHA256}
    assert retrieval["supplements_retrieved"] == retrieval["code_repositories_retrieved"] == 0
    assert retrieval["datasets_retrieved"] == retrieval["model_weights_retrieved"] == 0
    r566 = record(packet(), "R566")["scientific_evidence"]["retrieval_accounting"]
    assert r566["complete_unique_manuscripts"] == 1 and r566["PDF_http_GET_requests"] == 2
    assert r566["initial_partial_request"]["complete_manuscripts"] == 0
    assert r566["continuation"]["http_code"] == 206
    assert r566["continuation"]["etag_matches_initial"] is True
    assert r566["continuation"]["content_range"] == "bytes 1190618-2097561/2097562"
    assert r566["complete_pdf"]["sha256"] == PDF_SHA256


def test_only_R566_closes_and_distinct_pending_papers_are_derived_from_the_ledger():
    before = accounting(csv_records(published_bytes(BASE, DECISIONS)), published_context(BASE)["papers"])
    rows = csv_records(published_bytes(PUBLISHED, DECISIONS))
    after = accounting(rows, published_context(PUBLISHED)["papers"])
    assert after == packet()["batch_b_accounting"]
    assert before["historical_actions"] == after["historical_actions"] == 159
    assert before["historical_papers"] == after["historical_papers"] == 148
    assert [before[key] for key in ("historical_unresolved_actions", "active_public_unresolved_actions",
                                   "active_public_unresolved_papers")] == [148, 146, 135]
    assert [after[key] for key in ("historical_unresolved_actions", "active_public_unresolved_actions",
                                  "active_public_unresolved_papers")] == [147, 145, 134]
    assert set(after["closed_review_ids"]) - set(before["closed_review_ids"]) == {"R566"}
    assert before["closed_review_ids"] == original()["batch_b_accounting"]["resolved_review_ids"]
    assert after["historical_unresolved_review_ids"] == [
        rid for rid in before["historical_unresolved_review_ids"] if rid != "R566"]
    assert after["active_public_unresolved_review_ids"] == [
        rid for rid in before["active_public_unresolved_review_ids"] if rid != "R566"]
    assert {"R267", "T046", "T093", "T608", "T526", "P526"} <= set(after["active_public_unresolved_review_ids"])
    ledger = [row for row in decision_rows(load_queues()) if row["batch"] == "B"]
    assert [row["review_id"] for row in ledger if row["paper_id"] == R566] == ["R566"]
    assert not [row for row in ledger if row["paper_id"] == R566 and row["review_id"] not in terminal(rows)]
    live = read_review_decisions(ROOT / DECISIONS)
    assert terminal(live)["R566"] == DECISION_ID
    assert {"T046", "T093", "T608", "T526", "P526"} <= set(
        accounting(live)["active_public_unresolved_review_ids"])
    assert "R267" in accounting(rows, published_context(PUBLISHED)["papers"])["active_public_unresolved_review_ids"]


def test_original_questions_locked_policy_and_unrelated_authoritative_tables_are_immutable():
    queues = load_queues()
    taxonomy = {row["review_id"]: row for row in queues["taxonomy_review"]["records"]}
    for review_id in ("R267", "R566"):
        assert record(packet(), review_id)["original_review"] == taxonomy[review_id]
    policy_path = AUDIT + "batch_c_policy_decisions.json"
    policies = json.loads((ROOT / policy_path).read_bytes())["policies"]
    assert packet()["locked_policies"] == [row for row in policies if row["policy_id"].startswith("R")]
    for name in ("taxonomy_review", "publication_metadata_review", "relationship_review", "unmapped_papers",
                 "batch_c_policy_decisions"):
        path = AUDIT + name + ".json"
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path
    # These three publication-dependent tables now have an approved B5 successor.
    # Check their original transaction at its immutable endpoint; every other
    # path, original question and locked policy remains a live byte guard.
    publication_successor_paths = {
        "data/curated/publication_overrides.csv",
        "data/curated/venue_aliases.csv",
        "data/manual/missing_author_mappings_report.csv",
    }
    allowed = {PAPERS, TAXONOMY, DECISIONS, *PUBLIC}
    for path in baseline_paths("data/curated", "data/manual", "web/data"):
        if path not in allowed:
            observed = published_bytes(PUBLISHED, path) if path in publication_successor_paths else (ROOT / path).read_bytes()
            assert observed == published_bytes(BASE, path), path


def test_historical_and_current_source_hashes_are_separate_and_portable():
    old, new = original(), packet()
    assert new["source_files_sha256"] == old["source_files_sha256"]
    current = new["current_source_sha256"]
    assert current.keys() == old["source_files_sha256"].keys()
    assert {path for path in current if current[path] != old["source_files_sha256"][path]} == {
        PAPERS, TAXONOMY, DECISIONS, *PUBLIC}
    tracked = set(baseline_paths())
    entries = {row["path"]: row for row in json.loads(published_bytes(BASE, FIXTURES))["entries"]}
    for path, expected in current.items():
        if path in tracked:
            raw = published_bytes(PUBLISHED, path)
        else:
            # Authenticate ignored historical data from its committed snapshot;
            # a developer's populated runtime-cache path is not a test dependency.
            entry = entries[path]
            assert entry["compression"] == "none"
            raw = published_bytes(BASE, entry["source"])
            assert digest(raw) == entry["sha256"] == entry["source_sha256"]
            assert len(raw) == entry["bytes"]
        assert digest(raw) == expected, path


def test_all_fourteen_prior_B_receipts_and_committed_historical_fixtures_keep_exact_bytes():
    receipts = original()["preservation"]["prior_B1A_to_B1G_artifact_sha256"]
    assert len(receipts) == 14
    for path, expected in receipts.items():
        assert digest(published_bytes(BASE, path)) == expected
        assert digest((ROOT / path).read_bytes()) == expected, path
    fixtures = baseline_paths("tests/fixtures")
    assert FIXTURES in fixtures
    for path in fixtures:
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_all_49_frozen_neurips_payloads_and_migration_status_remain_exact():
    path = "data/raw/systematic_gap_migration_2026_10_03/baseline.json"
    raw = (ROOT / path).read_bytes()
    assert raw == published_bytes(BASE, path)
    frozen = json.loads(raw)["frozen_sha256"]
    assert len(frozen) == 49
    for relative, expected in frozen.items():
        assert digest(preserved_bytes(ROOT, relative)) == expected, relative
    assert packet()["neurips_status"] == "7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA"


def test_C13_and_separate_39_paper_inventory_are_preserved_outside_the_original_B_ledger():
    data, old = packet(), original()
    assert data["batch_c_deferred_accounting"] == old["batch_c_deferred_accounting"]
    debts = data["batch_c_deferred_accounting"]
    assert debts["total_actions"] == 41 and debts["resolved"] == 28
    assert debts["total_unresolved"] == debts["external_unresolved"] == 13
    assert debts["maintainer_judgments"] == 0 and len(debts["remaining_external_ids"]) == 13
    assert data["separate_import_review_inventory"] == old["separate_import_review_inventory"]
    intake = data["separate_import_review_inventory"]
    assert intake["imported_affiliation_debt_papers"] == 39
    assert intake["overlapping_taxonomy_review_papers"] == 14 and intake["held_candidates"] == 12
    assert intake["original_B_inventory_not_combined"] is True
    for path in C13_FILES:
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_report_and_packet_record_the_bounded_correction_and_unresolved_case_consistently():
    data, report = packet(), (ROOT / REPORT).read_text()
    assert data["scope"]["review_decisions_added"] == data["scope"]["review_actions_closed"] == 1
    assert data["scope"]["authoritative_scientific_changes"] == 1
    assert data["scope"]["forensic_task_changes"] == 0
    # Export/full-suite counters are completion receipts; they may legitimately
    # advance after this focused test runs and are not classification invariants.
    for token in (DECISION_ID, "R566", "R267", "analysis_study", "PROPOSE_CORRECTION_ACCEPTED",
                  "EVIDENCE_STILL_INSUFFICIENT", "147", "145", "134", BASE,
                  "7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA"):
        assert token in report
    assert "accepted" in report.casefold() and "terminal decision" in report.casefold()
    assert "IEEE" in report and "arXiv" in report and "unverified" in report
    assert data["adjudication"]["decision_id"] == DECISION_ID
