"""B1K removes one unsupported benchmark role while preserving a blocked case."""
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
from tests.baseline_expectations import CURRENT_CORPUS_COUNTS, CURRENT_TAXONOMY_TOTALS
from tests.corpus_quality_test_helpers import csv_records, published_bytes, published_context

ROOT = Path(__file__).resolve().parents[1]
BASE = "b2f17505f2d3a1b65d43fcf3c6582436b4fe44f8"
PAPERS = "data/curated/papers.csv"
TAXONOMY = "data/curated/paper_taxonomy.csv"
DECISIONS = "data/curated/review_decisions.csv"
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1k_2026_10_22/evidence_manifest.json"
REPORT = "docs/corpus_quality_batch_b_wave_b1k_2026_10_22.md"
AUDIT = "data/raw/corpus_quality_audit_2026_10_04/"
FIXTURES = "tests/fixtures/historical_test_fixture_manifest.json"
TARGET = "doi:10.3390/app131910980"
DEFERRED = "doi:10.3390/ai5030076"
DECISION_ID = "review:1691b3f56711c58a7861"
CSV_UPDATES = {'research_types': 'survey',
 'research_types_review_reason': 'R542 PROPOSE_CORRECTION_ACCEPTED under locked R2: the complete '
                                 '36-page DOI-matched institutional publisher-formatted manuscript '
                                 'substantiates survey synthesis of existing methods, datasets, '
                                 'metrics and source-attributed comparisons, but does not '
                                 'sufficiently establish a distinct substantive reusable benchmark '
                                 'contribution. Remove benchmark; retain survey, detection and all '
                                 'existing image scopes. This is a medium-confidence '
                                 'contribution-level judgment, not an automatic survey '
                                 'disqualification or a mandatory-code/new-data rule. Preserve the '
                                 'first-person Fakeddit two-way-label experiment statement, '
                                 'explicit performance-comparison contribution and '
                                 'same-dataset/metric design as positive counterevidence '
                                 'supporting a permissive framework interpretation. No claim is '
                                 'made that no experiments ever occurred. The claimed experiment '
                                 'is not tied to a specified model, split, scoring protocol or '
                                 'Fakeddit result. Numeric, citation, catalog and printed metric '
                                 'ambiguities remain unresolved. The inaccessible direct MDPI PDF '
                                 'was not byte-compared; publisher-version equivalence and later '
                                 'corrections are unverified.',
 'research_types_evidence_tier': 'primary_paper',
 'research_types_evidence_source': 'https://www.um.edu.mt/library/oar/bitstream/123456789/123188/1/A%20survey%20of%20detection%20and%20mitigation%20for%20fake%20images%20on%20social%20media%20platforms%202023.pdf',
 'research_types_evidence_excerpt': 'Applied Sciences 2023, 13(19), 10980, institutional '
                                    'publisher-formatted copy: section 1.3 p.4 claims a '
                                    'performance comparison; section 4 p.8 groups cited methods by '
                                    'dataset/metric; Tables 1-7 attribute source results, with '
                                    'p.25 explicitly taking att-RNN results from Khattar. Tables '
                                    '8-9 pp.26-27 summarize existing confusion-matrix metrics, '
                                    'Table 10 p.28 catalogs 14 external datasets, and p.31 points '
                                    'to referenced public resources. Section 6.2 p.27 states '
                                    'first-person selection of two-way fake/real labels in an '
                                    'experiment; that real counterevidence is preserved, but no '
                                    'linked Fakeddit protocol or results establishes a separately '
                                    'substantive reusable benchmark. Same-dataset/metric '
                                    'comparisons support a competing permissive R2 interpretation. '
                                    'Retain survey only at medium confidence; preserve all printed '
                                    'numerical/citation/catalog/metric issues and unverified '
                                    'equivalence to the blocked MDPI PDF.',
 'audited_at': '2026-10-22'}
CSV_AFTER_HASH = "a7ff2ff4ea9357ab47ea2e0e966c7ac303fb428b0b2635953fe8b1ddb72703ce"
EVIDENCE_HASHES = {
    "manifest": "ab1af931d528e0ad2bc8d907054c77945c81ae720a2a7babf73afc4f5bac02b2",
    "report": "fd19be2941b76e2764b184940b8bd7847e5486ab62987389231a3bbe390739ae",
}
WORKER_HASHES = {
    "R467": "37e4e96b2e28ae7488688e5d5220592b7b5c41e1fe705e7af89059ae231747df",
    "R542": "9986c5180b4eb0578c6c02982f5b5ed1b1fc7d26006b73472e565819fa63267f",
}
R542_PDF_SHA = "430e00965954d8c1d69f017c70e567b12a973691fe8b2bd6825276a154f82ef9"
R467_PARTIAL_SHA = "d129dc07bd121a6b22f08b52f1a19193776e66fe8b6f88e5d11dbfb97fcc85d0"


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
    found = [row for row in data["records"] if row["review_id"] == review_id]
    assert len(found) == 1
    return found[0]


def terminal(rows):
    result = {}
    for row in rows:
        match = re.search(r"\bBatch B review ([A-Z]\d{3});", row["review_note"])
        if match and row["action"] == "no_action_after_review":
            assert match[1] not in result, "Duplicate original-action terminal decision"
            result[match[1]] = row["decision_id"]
    return result


def taxonomy_row(raw, taxonomy_id):
    rows = [r for r in csv_records(raw) if r["taxonomy_id"] == taxonomy_id]
    assert len(rows) == 1
    return rows[0]


@lru_cache
def baseline_paths(*prefixes):
    return subprocess.check_output(
        ["git", "--no-optional-locks", "ls-tree", "-r", "--name-only", BASE,
         "--", *prefixes], cwd=ROOT, text=True).splitlines()


def logical_csv_chunks(raw):
    lines = raw.splitlines(keepends=True)
    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    chunks, start = [], 0
    for _ in reader:
        chunks.append(b"".join(lines[start:reader.line_num]))
        start = reader.line_num
    assert start == len(lines)
    return chunks


def replace_csv_tokens(raw, header, updates):
    """Replace only reviewed CSV cells, retaining all other bytes verbatim."""
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


def accounting(rows, public):
    ledger = [r for r in decision_rows(load_queues()) if r["batch"] == "B"]
    done = terminal(rows)
    pending = [r for r in ledger if r["review_id"] not in done]
    active = [r for r in pending if r["paper_id"] in public]
    return {
        "historical_actions": len(ledger),
        "historical_papers": len({r["paper_id"] for r in ledger}),
        "closed_review_ids": sorted(done),
        "historical_unresolved_actions": len(pending),
        "historical_unresolved_papers": len({r["paper_id"] for r in pending}),
        "active_public_unresolved_actions": len(active),
        "active_public_unresolved_papers": len({r["paper_id"] for r in active}),
        "historical_unresolved_review_ids": [r["review_id"] for r in pending],
        "active_public_unresolved_review_ids": [r["review_id"] for r in active],
    }


@pytest.mark.parametrize("kind", ["manifest", "report"])
def test_complete_evidence_stage_packet_is_portable_and_hash_exact(kind):
    assert archived_bytes(kind)
    assert set(packet()["evidence_only_packet_archives"]) == {"manifest", "report"}
    assert packet()["baseline_commit"] == BASE
    assert original()["phase"] == "EVIDENCE_ONLY_READY_FOR_MAINTAINER_ADJUDICATION"


def test_worker_check_notation_is_two_distinct_verified_counts_not_a_ratio():
    validation = original()["validation"]
    assert validation["status"] == "PASS"
    receipts = validation["lightweight_checks"]
    expected = {"R467_worker": 38, "R542_worker": 35, "root_spotchecks": 20,
                "R542_independent": 52, "preservation": 38, "packet": 36}
    for key, count in expected.items():
        receipt = receipts[key]["receipt"]
        assert receipt["passed"] == count and receipt["failed"] == 0
        assert len(receipt["checks"]) == count
        assert all(c["passed"] is True for c in receipt["checks"])
    assert sum(receipts[k]["receipt"]["passed"] for k in ("R467_worker", "R542_worker")) == 73
    assert packet()["evidence_only_validation"] == validation


def test_only_six_cells_in_one_legacy_taxonomy_row_change_without_any_other_token_churn():
    before_raw, after_raw = published_bytes(BASE, TAXONOMY), (ROOT / TAXONOMY).read_bytes()
    before, after = csv_records(before_raw), csv_records(after_raw)
    assert [r["taxonomy_id"] for r in before] == [r["taxonomy_id"] for r in after]
    assert len({r["taxonomy_id"] for r in after}) == len(after)
    assert {old["taxonomy_id"] for old, new in zip(before, after) if old != new} == {TARGET}
    old, new = taxonomy_row(before_raw, TARGET), taxonomy_row(after_raw, TARGET)
    assert old["paper_id"] == new["paper_id"] == ""
    assert old["research_types"] == "benchmark;survey" and new["research_types"] == "survey"
    assert set(CSV_UPDATES) == {"research_types", "research_types_review_reason", "research_types_evidence_tier",
                                "research_types_evidence_source", "research_types_evidence_excerpt", "audited_at"}
    assert {k for k in old if old[k] != new[k]} == CSV_UPDATES.keys()
    assert new == {**old, **CSV_UPDATES}
    assert new["tasks"] == old["tasks"] == "detection"
    assert new["image_scopes"] == old["image_scopes"] == "fully_generated;deepfake;traditional_manipulation"
    assert new["research_types_status"] == old["research_types_status"] == "reviewed"
    assert new["research_types_evidence_tier"] == "primary_paper" and new["audited_at"] == "2026-10-22"
    header = next(csv.reader(io.StringIO(before_raw.decode(), newline="")))
    chunks = logical_csv_chunks(before_raw)
    expected = [chunks[0]] + [replace_csv_tokens(chunk, header, CSV_UPDATES) if row["taxonomy_id"] == TARGET else chunk
                              for row, chunk in zip(before, chunks[1:])]
    assert after_raw == b"".join(expected)
    assert digest(after_raw) == CSV_AFTER_HASH
    assert (ROOT / PAPERS).read_bytes() == published_bytes(BASE, PAPERS)
    assert not [r for r in csv_records((ROOT / PAPERS).read_bytes()) if r["doi"] == TARGET.removeprefix("doi:")]


def test_one_terminal_append_preserves_all_91_previous_rows_and_bytes():
    before, after = published_bytes(BASE, DECISIONS), (ROOT / DECISIONS).read_bytes()
    old, rows = csv_records(before), read_review_decisions(ROOT / DECISIONS)
    assert after.startswith(before) and rows[:-1] == old
    assert len(old) == 91 and len(rows) == 92
    assert len({r["decision_id"] for r in rows}) == len(rows)
    assert terminal(rows) == {**terminal(old), "R542": DECISION_ID}
    row = rows[-1]
    assert row["decision_id"] == DECISION_ID
    assert row["review_queue"] == "other" and row["review_queue"] in ALLOWED_REVIEW_QUEUES
    assert row["action"] == "no_action_after_review" and row["action"] in ALLOWED_REVIEW_ACTIONS
    assert row["target_type"] == "paper" and row["institution"] == ""
    assert row["created_by"] == "maintainer-approved-batch-b-b1k"
    assert row["created_at"] == row["updated_at"] and row["created_at"].startswith("2026-10-22T")
    assert datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")).tzinfo == timezone.utc
    prior = taxonomy_row(published_bytes(BASE, TAXONOMY), TARGET)
    for key in ("title", "year", "doi", "openalex_url"):
        assert row[key] == prior[key]
    identity = "|".join(" ".join(row[k].split()).casefold() for k in
                        ("review_queue", "target_type", "doi", "openalex_url", "title", "year", "institution"))
    assert "review:" + digest(identity.encode())[:20] == DECISION_ID
    note = row["review_note"]
    assert note.startswith("Batch B review R542;") and "PROPOSE_CORRECTION_ACCEPTED" in note
    assert R542_PDF_SHA in note
    for token in ("R2", "Fakeddit", "medium", "survey", "benchmark"):
        assert token in note
    assert "R467" not in terminal(rows) and "P467" not in terminal(rows)
    adjudication = packet()["adjudication"]
    assert adjudication["decision_ids"] == {"R542": DECISION_ID}
    assert adjudication["terminal_decisions"] == {"R542": row}
    assert adjudication["registry_rows_before"] == 91 and adjudication["registry_rows_after"] == 92
    assert adjudication["prior_decision_bytes_preserved"] is True
    assert adjudication["before_registry_sha256"] == digest(before)
    assert adjudication["after_registry_sha256"] == digest(after)
    assert adjudication["existing_csv_cells_changed"] == 6
    changes = adjudication["csv_changes"]
    assert len(changes) == 1 and changes[0]["path"] == TAXONOMY
    assert changes[0]["row_identity"]["taxonomy_id"] == TARGET
    assert changes[0]["after_fields"] == CSV_UPDATES and changes[0]["planned_after_sha256"] == CSV_AFTER_HASH


def test_terminal_upsert_is_idempotent_without_timestamp_or_byte_churn(tmp_path):
    path = tmp_path / "review_decisions.csv"
    raw = (ROOT / DECISIONS).read_bytes()
    path.write_bytes(raw)
    row = next(r for r in read_review_decisions(path) if r["decision_id"] == DECISION_ID)
    assert upsert_review_decision(row, path=path) == row
    assert path.read_bytes() == raw


def test_only_R542_closes_and_distinct_affected_public_papers_are_derived_from_original_ledger():
    ledger = [r for r in decision_rows(load_queues()) if r["batch"] == "B"]
    before = accounting(csv_records(published_bytes(BASE, DECISIONS)), published_context(BASE)["papers"])
    after = accounting(read_review_decisions(ROOT / DECISIONS), load_context()["papers"])
    assert after == packet()["batch_b_accounting"]
    keys = ("historical_actions", "historical_papers", "historical_unresolved_actions",
            "active_public_unresolved_actions", "active_public_unresolved_papers")
    assert [before[k] for k in keys] == [159, 148, 143, 141, 130]
    assert [after[k] for k in keys] == [159, 148, 142, 140, 129]
    assert before["historical_unresolved_papers"] == 132 and after["historical_unresolved_papers"] == 131
    assert set(after["closed_review_ids"]) - set(before["closed_review_ids"]) == {"R542"}
    for key in ("historical_unresolved_review_ids", "active_public_unresolved_review_ids"):
        assert after[key] == [rid for rid in before[key] if rid != "R542"]
        assert {"R467", "P467", "R267", "T046", "T093", "T608", "T526", "P526"} <= set(after[key])
    assert [(r["review_id"],r["dimension"]) for r in ledger if r["paper_id"] == TARGET] == [("R542", "research_types")]
    assert {(r["review_id"],r.get("dimension","publication")) for r in ledger if r["paper_id"] == DEFERRED} == {
        ("R467", "research_types"), ("P467", "publication")}


def test_original_scientific_records_remain_lossless_with_only_R542_acceptance_flags_changed():
    old, new = original(), packet()
    assert [r["review_id"] for r in new["records"]] == ["R467", "R542"]
    assert record(new,"R467") == record(old,"R467")
    flags = {"maintainer_acceptance_pending", "review_closed", "authoritative_changes_applied", "terminal_review_decision_created"}
    prior, accepted = record(old,"R542"), record(new,"R542")
    for key in prior:
        if key not in flags:
            assert accepted[key] == prior[key], key
    assert accepted["maintainer_acceptance_pending"] is False
    assert all(accepted[k] is True for k in flags - {"maintainer_acceptance_pending"})
    assert accepted["terminal_review_decision_id"] == DECISION_ID
    assert accepted["accepted_outcome"] == "PROPOSE_CORRECTION_ACCEPTED"
    assert accepted["final_authoritative_taxonomy"] == {
        "tasks":["detection"], "image_scopes":["fully_generated","deepfake","traditional_manipulation"], "research_types":["survey"]}
    for rid in ("R467", "R542"):
        assert record(new,rid)["scientific_review"] == record(old,rid)["scientific_review"]
        assert record(new,rid)["worker_review_sha256"] == WORKER_HASHES[rid]
    for key in ("retrieval_accounting", "locked_policy_ledger", "R1_observation_policy", "precedent_decisions",
                "policy_interpretation", "source_files_sha256", "prior_B1A_J_artifact_sha256", "worker_artifact_sha256",
                "root_scientific_spotchecks", "independent_scientific_reviews", "batch_c_deferred_accounting",
                "separate_import_review_inventory", "preservation", "operational_baseline"):
        assert new[key] == old[key], key
    for key in ("scope", "validation", "integrity", "corpus_counts", "taxonomy_counts", "batch_b_accounting",
                "accounting_effect", "final_git_requirements", "final_git_observation", "phase"):
        assert new["evidence_only_"+key] == old[key], key


def test_R542_complete_institutional_source_is_not_claimed_to_be_the_blocked_publisher_bytes():
    scientific = record(packet(),"R542")["scientific_review"]
    source = scientific["source"]
    assert source["sha256"] == R542_PDF_SHA and source["bytes"] == 4761099 and source["pages"] == 36
    assert source["url"].startswith("https://www.um.edu.mt/library/oar/bitstream/")
    assert source["full_manuscript_read"] is True and source["pages_read"] == list(range(1,37))
    assert source["tables_read"] == list(range(1,11)) and len(scientific["authors"]) == 6
    for token in ("publisher-formatted", "blocked", "not independently established"):
        assert token in source["version"]
    assert scientific["canonical_paper_id"] == TARGET
    assert scientific["provisional_outcome"] == "BENCHMARK_REMOVAL_SUPPORTED"
    assert scientific["proposed_complete_research_types"] == ["survey"]
    assert "Medium" in scientific["confidence"]["overall_R2_provisional_removal"]
    assert len(scientific["question_matrix"]) == 12 and len(scientific["all_table_inventory"]) == 10


def test_R542_prior_study_values_and_citation_metric_dataset_inconsistencies_are_preserved():
    scientific = record(packet(),"R542")["scientific_review"]
    q = scientific["quantitative_evidence"]
    assert "not evidence of newly run survey benchmarks" in q["attribution_boundary"]
    assert q["Table6"]["column_order"] == ["Columbia","CASIA1.0","CASIA2.0","NIST16"]
    assert next(r for r in q["Table6"]["rows"] if r["framework"] == "RRU-Net") == {
        "source_reference":96,"author":"Bi et al.","framework":"RRU-Net","F1":[0.915,None,0.841,None]}
    assert q["Table7"]["column_order"] == ["MediaEval","Weibo"]
    rows = {r["framework"]:r for r in q["Table7"]["rows"]}
    assert rows["SAFE"]["accuracy_values"] == [87.4,83.8]
    assert rows["SpotFake"]["accuracy_values"] == [77.77,89.23]
    assert rows["att-RNN"]["source_reference_as_printed"] == rows["EANN"]["source_reference_as_printed"] == 129
    assert q["Table7"]["source_attribution_explicit_p25"] is True
    assert q["Table7"]["Fakeddit_column_present"] is False
    assert q["Table9"]["formula_grouping_uncertainty_preserved"] is True
    limitations = " ".join(scientific["limitations_and_competing_evidence"])
    for token in ("92.08/95.70", "94.19/96.61", "89.76", "COCO", "Copydays", "EfficientNet", "RoBERTa"):
        assert token in limitations


def test_R542_first_person_experiment_and_same_dataset_counterevidence_are_not_erased():
    scientific = record(packet(),"R542")["scientific_review"]
    empirical = scientific["empirical_execution_assessment"]
    assert empirical["categorical_no_experiments_claim"] is False
    counter = empirical["Fakeddit_first_person_counterevidence"]
    assert counter["locator"] == "§6.2 p.27, visually checked"
    assert counter["short_exact_quote"] == "In the experiment, we have selected a two-way labeling of fake vs. real."
    assert counter["original_benchmark_automatically_inferred"] is False
    assert empirical["independent_rerun_established"] is False
    assert empirical["reviewed_cited_papers_downloaded"] == 0
    retention = " ".join(x["evidence"] for x in scientific["benchmark_retention_evidence"])
    for token in ("performance comparison", "same metric/dataset", "Fakeddit"):
        assert token in retention
    assert scientific["relevant_precedents"]["no_mandatory_new_code_dataset_or_experiment_condition"] is True
    assert "systematic comparative framework" in scientific["locked_R2_policy"]["final_rule"]
    assert scientific["R2_assessment"]["permissive_competing_interpretation"]


def test_R467_all_scientific_and_authoritative_context_remains_unchanged_and_unresolved():
    old, new = published_context(BASE), load_context()
    assert old["papers"][DEFERRED] == new["papers"][DEFERRED]
    assert sum(n for (pid,_),n in old["pairs"].items() if pid == DEFERRED) == 2
    assert {pair:n for pair,n in old["pairs"].items() if pair[0] == DEFERRED} == {
        pair:n for pair,n in new["pairs"].items() if pair[0] == DEFERRED}
    assert old["taxonomy"][DEFERRED] == new["taxonomy"][DEFERRED]
    assert taxonomy_row(published_bytes(BASE,TAXONOMY),DEFERRED) == taxonomy_row((ROOT/TAXONOMY).read_bytes(),DEFERRED)
    assert new["papers"][DEFERRED]["research_types"] == ["method","benchmark"]
    assert new["papers"][DEFERRED]["tasks"] == ["detection"]
    r = record(packet(),"R467")
    assert r == record(original(),"R467")
    assert r["provisional_outcome"] == "EVIDENCE_STILL_INSUFFICIENT"
    assert r["review_closed"] is False and r["terminal_review_decision_created"] is False
    assert r["scientific_evidence_sufficient"] is False
    assert r["authoritative_changes_applied"] is False
    assert {"R467","P467"} <= set(packet()["batch_b_accounting"]["active_public_unresolved_review_ids"])


def test_R467_partial_source_denials_missing_tables_and_version_uncertainty_are_preserved():
    scientific = record(packet(),"R467")["scientific_review"]
    source = scientific["source"]
    assert source["partial_PDF_sha256"] == R467_PARTIAL_SHA
    assert source["partial_PDF_bytes"] == 15024008 and source["expected_institution_file_bytes"] == 38629090
    assert source["whole_file_MD5_verified"] is False and source["full_manuscript_read"] is False
    assert all(source[k] is None for k in ("whole_manuscript_sha256","whole_manuscript_bytes","readable_complete_PDF_pages"))
    assert source["complete_PDF_obtained"] is source["complete_HTML_obtained"] is False
    assert source["published_page_count_only"] == 19
    assert len(scientific["question_matrix"]) == 14
    q = scientific["quantitative_evidence"]
    assert q["verified_complete_experimental_tables"] == []
    assert q["abstract_only_accuracy_claim"]["accuracy_percent"] == 97.32
    assert q["abstract_only_accuracy_claim"]["verified_against_experimental_table"] is False
    a = scientific["retrieval_accounting"]
    assert a["official_PDF_http_status"] == a["root_XML_check"]["http_status"] == 403
    assert a["institution_initial_curl_exit_code"] == 28
    assert a["institution_range_http_status"] == 200 and a["institution_range_curl_exit_code"] == 63
    assert a["institution_range_body_bytes"] == 0 and a["institution_range_ignored_and_not_appended"] is True
    assert a["root_XML_check"]["content_type"] == "text/html" and a["root_XML_check"]["complete_manuscript"] is False
    assert "HTTP429" in a["web_metadata_history"][0]["result"]


def test_R467_satellite_observation_is_provisional_out_of_scope_not_a_dataset_or_review_addition():
    scientific = record(packet(),"R467")["scientific_review"]
    o = scientific["out_of_scope_dataset_taxonomy_observation"]
    assert o["label"] == "OUT_OF_SCOPE_DATASET_TAXONOMY_OBSERVATION"
    assert o["independent_R1_dataset_contribution_established"] is False
    assert o["dataset_addition_proposed_in_this_wave"] is False and o["new_Batch_B_actions_added"] == 0
    assert o["tasks_changed"] is o["image_scopes_changed"] is False
    q = scientific["quantitative_evidence"]
    prep = q["partial_data_preparation_claims"]
    assert prep["original_clean_satellite_slices"] == prep["transformed_training_variants"] == 50000
    assert prep["GAN_training_examples_including_augmentation"] == 100000
    assert prep["must_not_conflate_transformed_variants_with_StyleGAN_outputs"] is True
    assert q["independent_50000_real_plus_50000_generated_detection_dataset_verified"] is False
    assert scientific["proposed_complete_research_types"] == ["method","benchmark"]
    assert "hold" in scientific["proposal_semantics"].casefold()


def test_one_complete_R542_and_zero_complete_R467_sources_remain_separate_without_new_retrieval():
    a = packet()["retrieval_accounting"]
    assert a == original()["retrieval_accounting"]
    assert a["new_complete_manuscripts_by_review"] == {"R467":0,"R542":1}
    assert a["new_complete_manuscripts_total"] == a["distinct_complete_versions_total"] == 1
    assert a["new_complete_manuscripts_retrieved_by_root"] == 0
    assert packet()["adjudication"]["scientific_source_retrievals_during_adjudication"] == 0
    r542 = a["per_review"]["R542"]
    assert r542["publisher_PDF_HTTP_status"] == 403 and r542["institutional_PDF_HTTP_status"] == 200
    assert r542["institutional_PDF_response_body_bytes"] == 4761099
    assert r542["repeated_inaccessible_endpoint_retries"] == 0
    assert all(r542[k] == 0 for k in ("new_supplements","new_datasets_or_weights","new_code_or_repository_archives","other_papers_retrieved"))
    assert a["per_review"]["R467"]["new_complete_scientific_manuscripts"] == 0


def test_exact_one_existing_public_paper_and_six_dependent_maps_change_only_types_and_reason():
    old, live = published_context(BASE), load_context()
    assert old["papers"].keys() == live["papers"].keys() and len(live["papers"]) == 674
    assert {pid for pid in old["papers"] if old["papers"][pid] != live["papers"][pid]} == {TARGET}
    assert sum(old["papers"][pid] == live["papers"][pid] for pid in old["papers"] if pid != TARGET) == 673
    expected = deepcopy(old["papers"][TARGET])
    expected["research_types"] = ["survey"]
    expected["taxonomy_review"]["research_types"]["reason"] = CSV_UPDATES["research_types_review_reason"]
    assert live["papers"][TARGET] == expected
    assert old["pairs"] == live["pairs"] and sum(live["pairs"].values()) == len(live["pairs"]) == 1410
    for path in PUBLIC:
        before, after = json.loads(published_bytes(BASE,path)), json.loads((ROOT/path).read_bytes())
        oldmeta, newmeta = deepcopy(before["metadata"]), deepcopy(after["metadata"])
        oldmeta.pop("public_preview_generated_at",None); newmeta.pop("public_preview_generated_at",None)
        assert oldmeta == newmeta
        assert {k:v for k,v in before.items() if k not in {"records","metadata"}} == {k:v for k,v in after.items() if k not in {"records","metadata"}}
    before = {r["id"]:r for r in json.loads(published_bytes(BASE,PUBLIC[1]))["records"]}
    after = {r["id"]:r for r in json.loads((ROOT/PUBLIC[1]).read_bytes())["records"]}
    assert before.keys() == after.keys() and len(before) == 1410
    dependent = {key for key,row in before.items() if row.get("doi") == TARGET.removeprefix("doi:")}
    assert len(dependent) == 6
    assert {key for key in before if before[key] != after[key]} == dependent
    assert sum(before[k] == after[k] for k in before if k not in dependent) == 1404
    for key,row in before.items():
        expected = deepcopy(row)
        if key in dependent:
            expected["research_types"] = ["survey"]
            expected["taxonomy_review"]["research_types"]["reason"] = CSV_UPDATES["research_types_review_reason"]
        assert after[key] == expected, key


def test_recomputed_current_counts_change_only_benchmark_minus_one():
    old, live = published_context(BASE), load_context()
    assert old["counts"] == live["counts"] == packet()["corpus_counts"] == CURRENT_CORPUS_COUNTS
    def totals(context):
        return Counter(label for r in context["papers"].values() for dimension in ("tasks","research_types") for label in r[dimension])
    before, after = totals(old), totals(live)
    assert after == packet()["taxonomy_counts"] == CURRENT_TAXONOMY_TOTALS
    assert not after-before and before-after == {"benchmark":1}
    assert before["benchmark"] == 92 and after["benchmark"] == 91
    assert after == {"detection":621,"source_attribution":84,"localization":45,"method":578,
                     "dataset":135,"benchmark":91,"survey":21,"analysis_study":82}


def test_original_questions_policies_and_all_unrelated_authoritative_files_are_unchanged():
    queues = load_queues()
    original_rows = {r["review_id"]:r for r in queues["taxonomy_review"]["records"]}
    for rid in ("R467","R542"):
        assert record(packet(),rid)["original_review"] == original_rows[rid]
    assert packet()["locked_policy_ledger"] == original()["locked_policy_ledger"]
    allowed = {TAXONOMY,DECISIONS,*PUBLIC}
    for path in baseline_paths("data/curated","data/manual","web/data"):
        if path not in allowed:
            assert (ROOT/path).read_bytes() == published_bytes(BASE,path), path
    for name in ("taxonomy_review","publication_metadata_review","relationship_review","unmapped_papers","batch_c_policy_decisions"):
        path = AUDIT+name+".json"
        assert (ROOT/path).read_bytes() == published_bytes(BASE,path), path


def test_current_source_hashes_are_portable_and_change_only_authorized_dependencies():
    old,new = original(),packet()
    assert new["source_files_sha256"] == old["source_files_sha256"]
    current = new["current_source_sha256"]
    assert current.keys() == old["source_files_sha256"].keys()
    assert {p for p in current if current[p] != old["source_files_sha256"][p]} == {TAXONOMY,DECISIONS,*PUBLIC}
    tracked = set(baseline_paths())
    entries = {r["path"]:r for r in json.loads(published_bytes(BASE,FIXTURES))["entries"]}
    for path,expected in current.items():
        if path in tracked:
            raw = (ROOT/path).read_bytes()
        elif path in entries:
            entry = entries[path]
            assert entry["compression"] == "none"
            raw = published_bytes(BASE,entry["source"])
            assert digest(raw) == entry["sha256"] == entry["source_sha256"]
            assert len(raw) == entry["bytes"]
        else:
            # Literature-import reproduction inputs have a separate committed authority.
            raw = preserved_bytes(ROOT,path)
            preflight = json.loads(published_bytes(BASE,
                "data/processed/literature51_2026_10_16/followup/commit_preflight.json"))
            authority = preflight["reproduction_inputs"][path]
            assert len(raw) == authority["bytes"]
            assert digest(raw) == authority["original_sha256"] == old["source_files_sha256"][path]
        assert digest(raw) == expected, path


def test_all_twenty_prior_B_artifacts_and_historical_fixtures_are_immutable():
    prior = original()["prior_B1A_J_artifact_sha256"]
    assert len(prior) == 20
    for path,expected in prior.items():
        assert digest(published_bytes(BASE,path)) == digest((ROOT/path).read_bytes()) == expected, path
    for path in baseline_paths("tests/fixtures"):
        assert (ROOT/path).read_bytes() == published_bytes(BASE,path), path


def test_frozen_NeurIPS_C13_and_separate_39_inventory_are_untouched():
    path = "data/raw/systematic_gap_migration_2026_10_03/baseline.json"
    raw = (ROOT/path).read_bytes()
    assert raw == published_bytes(BASE,path)
    frozen = json.loads(raw)["frozen_sha256"]
    assert len(frozen) == 49
    for relative,expected in frozen.items():
        assert digest(preserved_bytes(ROOT,relative)) == expected, relative
    assert packet()["neurips_status"] == "7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA"
    debt = packet()["batch_c_deferred_accounting"]
    assert debt == original()["batch_c_deferred_accounting"]
    assert debt["total_actions"] == 41 and debt["resolved"] == 28
    assert debt["total_unresolved"] == debt["external_unresolved"] == 13
    assert debt["maintainer_judgments"] == 0 and len(debt["remaining_external_ids"]) == 13
    intake = packet()["separate_import_review_inventory"]
    assert intake == original()["separate_import_review_inventory"]
    assert intake["imported_papers"] == intake["unmapped"] == len(intake["candidate_to_paper"]) == 39
    assert intake["relationships"] == 0 and intake["taxonomy_pending"] == 14 and intake["held"] == 12
    live = load_context()
    for pid in intake["candidate_to_paper"].values():
        assert live["papers"][pid] == published_context(BASE)["papers"][pid]
        assert live["papers"][pid]["has_map_location"] is False
    for path in ("data/raw/corpus_quality_batch_c_closeout_2026_10_11/evidence_manifest.json",
                 "docs/corpus_quality_batch_c_closeout_2026_10_11.md",
                 "docs/corpus_quality_batch_c_evidence_debt_triage_2026_10_08.md",
                 "tests/test_corpus_quality_batch_c_closeout.py"):
        assert (ROOT/path).read_bytes() == published_bytes(BASE,path), path


def test_report_records_one_acceptance_and_one_open_review_and_preserves_original_report():
    data, report = packet(),(ROOT/REPORT).read_text()
    assert archived_bytes("report").decode() in report
    for token in (DECISION_ID,"R542","R467","P467","PROPOSE_CORRECTION_ACCEPTED","EVIDENCE_STILL_INSUFFICIENT",
                  "Fakeddit","142","140",BASE,"OUT_OF_SCOPE_DATASET_TAXONOMY_OBSERVATION",
                  "7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA"):
        assert token in report
    assert "medium" in report.casefold() and "unverified" in report.casefold()
    assert data["scope"]["review_decisions_added"] == data["scope"]["review_actions_closed"] == 1
    assert data["scope"]["authoritative_scientific_changes"] == 1
    assert data["scope"]["forensic_task_changes"] == data["scope"]["image_scope_changes"] == 0
    assert data["scope"]["new_Batch_B_actions_added"] == data["scope"]["Batch_B_denominator_changes"] == 0
