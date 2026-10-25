"""B1N accepts Attribution88's benchmark role and keeps atomic R234 unresolved."""
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
BASE = "05a89df9e5b3543c1231dc5934f55320aec53fa9"
PAPERS = "data/curated/papers.csv"
TAXONOMY = "data/curated/paper_taxonomy.csv"
DECISIONS = "data/curated/review_decisions.csv"
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1n_2026_10_24/evidence_manifest.json"
REPORT = "docs/corpus_quality_batch_b_wave_b1n_2026_10_24.md"
AUDIT = "data/raw/corpus_quality_audit_2026_10_04/"
FIXTURES = "tests/fixtures/historical_test_fixture_manifest.json"
TARGET = "curated:625ba11125534aedd39d"
DEFERRED = "curated:03f893b9484ea2d09c22"
DECISION_ID = "review:bec491a789b07af83e1e"
FINAL_TYPES = ["method", "dataset", "benchmark"]
PDF_SHA256 = "5fb6d9576126ad053381669f122ffcda440ffc1cb3e36954809de28aa9bceee0"
CODE_COMMIT = "b22608ffca12c38a9a13876f0f2e5268991b9afe"
# The following constants are filled from the frozen, reviewed transaction.
CSV_UPDATES = {'data/curated/papers.csv': {'research_types': 'method;dataset;benchmark'},
 'data/curated/paper_taxonomy.csv': {'research_types': 'method;dataset;benchmark',
                                     'research_types_review_reason': 'R596 accepted under locked R2: '
                                                                     'Attribution88 is a separately defined '
                                                                     'reusable evaluation '
                                                                     'benchmark/protocol/resource beyond '
                                                                     'RepMix and the retained dataset role. '
                                                                     'Eight fixed known source classes (Real '
                                                                     'plus seven GAN architectures), eleven '
                                                                     'semantic categories, six seen and five '
                                                                     'held-out semantics, '
                                                                     'per-source/semantic base partitions, '
                                                                     'nineteen corruptions at five '
                                                                     'severities and four held-out '
                                                                     'corruption types support independent '
                                                                     'source-attribution model evaluation. '
                                                                     'This meets R2 through structured task '
                                                                     'conditions, metrics and independent '
                                                                     'baselines, not scale or benchmark '
                                                                     'wording alone. Add benchmark; retain '
                                                                     'method, dataset, '
                                                                     'detection;source_attribution and '
                                                                     'fully_generated. High contribution '
                                                                     'confidence; medium operational '
                                                                     'reproducibility confidence. Labels '
                                                                     'identify architectures, not individual '
                                                                     'checkpoints; semantic-specific '
                                                                     'generator-instance change is coupled '
                                                                     'with semantic change inside a closed '
                                                                     'known-architecture label space, not an '
                                                                     'unknown-architecture open-set test. '
                                                                     'Detection is raw accuracy with nominal '
                                                                     'real/fake ratio 1:7, not balanced '
                                                                     'accuracy. Preserve nonuniform '
                                                                     'superiority, glass-blur '
                                                                     'counterexample, conditional '
                                                                     'generalization loss, '
                                                                     'adversarial-result rounding and '
                                                                     'paper/code early-stopping '
                                                                     'discrepancies. Full archive contents, '
                                                                     'actual CSV splits, upstream image '
                                                                     'rights, source-version equivalence and '
                                                                     'numerical reproduction remain '
                                                                     'unverified.',
                                     'research_types_evidence_tier': 'primary_paper',
                                     'research_types_evidence_source': 'https://www.ecva.net/papers/eccv_2022/papers_ECCV/papers/136740140.pdf',
                                     'research_types_evidence_excerpt': 'Official ECVA ECCV 2022 RepMix '
                                                                        'manuscript, sections 3 and 5, '
                                                                        'Tables 1-3 and Figures 3/7: '
                                                                        'Attribution88 declares 12,000 '
                                                                        'images per '
                                                                        'eight-source/eleven-semantic cell '
                                                                        '(1,056,000 base images), with '
                                                                        '10,000/1,000/1,000 '
                                                                        'train/validation/test per cell. Six '
                                                                        'training semantics and five '
                                                                        'held-out semantics; nineteen '
                                                                        'ImageNet-C types, five severities, '
                                                                        'four held-out types. Main '
                                                                        'detection/attribution accuracy/NMI: '
                                                                        'RepMix 0.9745/0.8207/0.6679 versus '
                                                                        'Yu reimplementation '
                                                                        '0.9306/0.6784/0.4666. Detection is '
                                                                        'raw real-versus-rest, not balanced; '
                                                                        'source labels include Real. '
                                                                        'Conditional attribution 0.9377 '
                                                                        'seen/seen versus 0.6505 '
                                                                        'unseen/unseen; glass-blur '
                                                                        'attribution about 0.67 versus Yu '
                                                                        '0.77. Fixed known GAN '
                                                                        'architectures, not '
                                                                        'unknown-generator open set. '
                                                                        'Repository '
                                                                        'b22608ffca12c38a9a13876f0f2e5268991b9afe '
                                                                        'advertises archives/splits and CC '
                                                                        'BY 4.0, without independent '
                                                                        'archive, split-membership, '
                                                                        'upstream-rights or reproduction '
                                                                        'verification. Separate '
                                                                        'Springer/arXiv full-version '
                                                                        'equivalence remains unverified.',
                                     'audited_at': '2026-10-25'}}
CSV_AFTER_HASHES = {'data/curated/papers.csv': 'e9030812061dd3a5779185fe951a24259c4c139f55ed85788fb0a8c1c45b9c82',
 'data/curated/paper_taxonomy.csv': '0caaea15b838dc1e085c4e735eb5bd00bbe3db889804356c8bd54c2ff01582d5'}
EVIDENCE_HASHES = {'manifest': '43665f1e08c5abc030697adfd823e15a97441c44d930dbac7ab34b797be3a1de',
 'report': '2c2b2b92f8eded6d99136eef6f776577d0794cbe62a1d0ea88046ec97416086f'}
QUANTITATIVE_SHA256 = 'e19f811ff15a0dbe24e71dd11594b35e517bdb9fe280476e7c65f23548a00155'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


@lru_cache
def packet():
    return json.loads((ROOT / MANIFEST).read_bytes())


def decode_archive(entry):
    assert entry["encoding"] == "gzip+base64"
    raw = gzip.decompress(base64.b64decode(entry["gzip_base64"], validate=True))
    assert len(raw) == entry["bytes"] and digest(raw) == entry["sha256"]
    return raw


@lru_cache
def archived_bytes(kind):
    raw = decode_archive(packet()["evidence_only_packet_archives"][kind])
    assert digest(raw) == EVIDENCE_HASHES[kind]
    return raw


@lru_cache
def original():
    return json.loads(archived_bytes("manifest"))


def record(data, review_id):
    found = [row for row in data["records"] if row["review_id"] == review_id]
    assert len(found) == 1
    return found[0]


def science(review_id):
    return record(packet(), review_id)["scientific_review"]


def selected_row(raw, paper_id):
    found = [row for row in csv_records(raw) if row["paper_id"] == paper_id]
    assert len(found) == 1
    return found[0]


def terminal(rows):
    result = {}
    for row in rows:
        match = re.search(r"\bBatch B review ([A-Z]\d{3});", row["review_note"])
        if match and row["action"] == "no_action_after_review":
            assert match[1] not in result, "Duplicate terminal original review"
            result[match[1]] = row["decision_id"]
    return result


def accounting(rows, public):
    ledger = [row for row in decision_rows(load_queues()) if row["batch"] == "B"]
    done = terminal(rows)
    pending = [row for row in ledger if row["review_id"] not in done]
    active = [row for row in pending if row["paper_id"] in public]
    return {
        "historical_actions": len(ledger), "historical_papers": len({row["paper_id"] for row in ledger}),
        "closed_review_ids": sorted(done),
        "historical_unresolved_actions": len(pending), "historical_unresolved_papers": len({row["paper_id"] for row in pending}),
        "active_public_unresolved_actions": len(active), "active_public_unresolved_papers": len({row["paper_id"] for row in active}),
        "historical_unresolved_review_ids": [row["review_id"] for row in pending],
        "active_public_unresolved_review_ids": [row["review_id"] for row in active],
    }


@lru_cache
def baseline_paths(*prefixes):
    return subprocess.check_output(["git", "--no-optional-locks", "ls-tree", "-r", "--name-only", BASE, "--", *prefixes], cwd=ROOT, text=True).splitlines()


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
    """Reconstruct only approved CSV tokens, preserving unrelated bytes."""
    spans, start, index, quoted = [], 0, 0, False
    while index < len(raw):
        byte = raw[index]
        if byte == 34:
            if quoted and index + 1 < len(raw) and raw[index + 1] == 34:
                index += 2
                continue
            quoted = not quoted
        elif not quoted and byte == 44:
            spans.append((start, index)); start = index + 1
        elif not quoted and byte in (10, 13):
            spans.append((start, index)); break
        index += 1
    else:
        spans.append((start, len(raw)))
    assert not quoted and len(spans) == len(header)
    edits = []
    for field, value in updates.items():
        stream = io.StringIO(newline="")
        csv.writer(stream, lineterminator="\n").writerow([value])
        edits.append((*spans[header.index(field)], stream.getvalue()[:-1].encode()))
    for begin, end, token in sorted(edits, reverse=True):
        raw = raw[:begin] + token + raw[end:]
    return raw


@pytest.mark.parametrize("kind", ["manifest", "report"])
def test_complete_evidence_only_packet_is_losslessly_preserved_and_portable(kind):
    assert archived_bytes(kind)
    assert set(packet()["evidence_only_packet_archives"]) == {"manifest", "report"}
    assert original()["baseline_commit"] == packet()["baseline_commit"] == BASE
    assert original()["scope"]["authoritative_data_changes"] == original()["scope"]["review_actions_closed"] == 0


def test_entire_original_scientific_records_timestamps_and_R234_outer_record_survive():
    old, new = original(), packet()
    assert [row["review_id"] for row in new["records"]] == ["R596", "R234"]
    flags = {"maintainer_acceptance_pending", "review_closed", "authoritative_changes_applied", "terminal_review_decision_created"}
    before, after = record(old, "R596"), record(new, "R596")
    assert {key: after[key] for key in before if key not in flags} == {key: value for key, value in before.items() if key not in flags}
    assert after["maintainer_acceptance_pending"] is False
    assert all(after[key] is True for key in flags - {"maintainer_acceptance_pending"})
    assert after["adjudication"]["accepted_policy"] == "R2"
    assert after["adjudication"]["decision_id"] == DECISION_ID
    assert after["terminal_review_decision_id"] == DECISION_ID
    assert after["accepted_outcome"] == "PROPOSE_CORRECTION_ACCEPTED"
    assert after["final_authoritative_taxonomy"] == {"tasks": ["detection", "source_attribution"], "image_scopes": ["fully_generated"], "research_types": FINAL_TYPES}
    assert record(old, "R234") == record(new, "R234")
    mutable = {"phase", "scope", "validation", "corpus_counts", "taxonomy_counts", "batch_b_accounting", "git_delivery"}
    for key in old:
        if key not in mutable | {"records"}:
            assert new[key] == old[key], key
    for key in mutable:
        assert new["evidence_only_" + key] == old[key], key


def test_original_worker_and_independent_checks_keep_their_distinct_actual_counts():
    old = original()
    assert old["validation"]["worker_checks"] == {"R596": {"passed": 50, "failed": 0}, "R234": {"passed": 60, "failed": 0}}
    assert old["validation"]["independent_scientific_checks"]["passed"] == 120
    assert old["validation"]["independent_source_provenance_checks"]["passed"] == 42
    assert old["validation"]["evidence_packet_checks"]["passed"] == 36
    assert old["validation"]["preservation_checks"]["passed"] == 43
    for rid, count in (("R596", 50), ("R234", 60)):
        receipt = old["independent_review"]["worker_validation"][rid]
        assert receipt["passed"] == count and receipt["failed"] == 0
        assert all(check["passed"] for check in receipt["checks"])
        assert record(packet(), rid)["frozen_worker_artifacts"] == record(old, rid)["frozen_worker_artifacts"]


@pytest.mark.parametrize("path", [PAPERS, TAXONOMY])
def test_exact_one_row_per_csv_and_seven_cells_change_with_all_other_tokens_identical(path):
    old_raw, new_raw = published_bytes(BASE, path), (ROOT / path).read_bytes()
    old, new = csv_records(old_raw), csv_records(new_raw)
    identity = "taxonomy_id" if path == TAXONOMY else "paper_id"
    assert [row[identity] for row in old] == [row[identity] for row in new]
    assert {row["paper_id"] for row, other in zip(old, new) if row != other} == {TARGET}
    before, after = selected_row(old_raw, TARGET), selected_row(new_raw, TARGET)
    updates = CSV_UPDATES[path]
    assert after == {**before, **updates}
    assert {key for key in before if before[key] != after[key]} == updates.keys()
    assert after["research_types"] == ";".join(FINAL_TYPES)
    assert before["tasks"] == after["tasks"] == "detection;source_attribution"
    assert before["image_scopes"] == after["image_scopes"] == "fully_generated"
    if path == PAPERS:
        assert set(updates) == {"research_types"}
    else:
        assert set(updates) == {"research_types", "research_types_review_reason", "research_types_evidence_tier", "research_types_evidence_source", "research_types_evidence_excerpt", "audited_at"}
        assert after["research_types_evidence_tier"] == "primary_paper"
        assert after["research_types_evidence_source"] == science("R596")["source"]["url"]
        assert after["audited_at"] == "2026-10-25" and after["research_types_status"] == before["research_types_status"] == "reviewed"
    header = next(csv.reader(io.StringIO(old_raw.decode(), newline="")))
    chunks = logical_csv_chunks(old_raw)
    expected = [chunks[0]]
    for row, chunk in zip(old, chunks[1:]):
        expected.append(replace_csv_tokens(chunk, header, updates) if row["paper_id"] == TARGET else chunk)
    assert new_raw == b"".join(expected)
    assert digest(new_raw) == CSV_AFTER_HASHES[path]
    assert selected_row(new_raw, DEFERRED) == selected_row(old_raw, DEFERRED)


def test_exact_one_R596_terminal_append_preserves_all_96_prior_rows_and_bytes():
    before, after = published_bytes(BASE, DECISIONS), (ROOT / DECISIONS).read_bytes()
    prior, rows = csv_records(before), read_review_decisions(ROOT / DECISIONS)
    assert after.startswith(before) and rows[:-1] == prior
    assert len(prior) == 96 and len(rows) == len({row["decision_id"] for row in rows}) == 97
    assert terminal(rows) == {**terminal(prior), "R596": DECISION_ID}
    assert "R234" not in terminal(rows)
    row = rows[-1]
    assert row["decision_id"] == DECISION_ID and row["review_queue"] == "other" and row["review_queue"] in ALLOWED_REVIEW_QUEUES
    assert row["action"] == "no_action_after_review" and row["action"] in ALLOWED_REVIEW_ACTIONS
    assert row["target_type"] == "paper" and row["institution"] == ""
    assert row["created_by"] == "maintainer-approved-batch-b-b1n"
    assert row["created_at"] == row["updated_at"]
    assert datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")).tzinfo == timezone.utc
    paper = selected_row(published_bytes(BASE, PAPERS), TARGET)
    assert all(row[key] == paper[key] for key in ("title", "year", "doi", "openalex_url"))
    identity = "|".join(" ".join(row[key].split()).casefold() for key in ("review_queue", "target_type", "doi", "openalex_url", "title", "year", "institution"))
    assert "review:" + digest(identity.encode())[:20] == DECISION_ID
    note = row["review_note"]
    assert note.startswith("Batch B review R596;")
    assert all(token in note for token in ("R2", "PROPOSE_CORRECTION_ACCEPTED", PDF_SHA256, "method;dataset", "method;dataset;benchmark", "0.9745", "0.8207", "0.6679"))
    assert packet()["adjudication"]["terminal_decisions"] == {"R596": row}
    transaction = packet()["adjudication"]
    assert transaction["deferred_review_ids"] == ["R234"]
    assert transaction["accepted_review_ids"] == ["R596"] and transaction["accepted_policy"] == "R2"
    assert transaction["registry_rows_before"] == 96 and transaction["registry_rows_after"] == 97
    assert transaction["before_registry_sha256"] == digest(before) and transaction["after_registry_sha256"] == digest(after)
    assert transaction["prior_decision_bytes_preserved"] is True
    assert transaction["existing_csv_cells_changed"] == transaction["total_existing_cells_changed"] == 7
    assert len(transaction["csv_changes"]) == 2
    assert transaction["csv_updates"] == {path: {"R596": fields} for path, fields in CSV_UPDATES.items()}
    for edit in transaction["csv_changes"]:
        assert edit["row_identity"] == {"paper_id": TARGET}
        assert edit["after_fields"] == CSV_UPDATES[edit["path"]]
        assert edit["planned_after_sha256"] == CSV_AFTER_HASHES[edit["path"]]
    deferred = transaction["R234_deferred"]
    assert deferred["R1"] == deferred["R2"] == "EVIDENCE_STILL_INSUFFICIENT"
    assert deferred["original_action_remains_open"] is True and deferred["scientific_no_change_confirmed"] is False
    assert deferred["authoritative_modifications"] == deferred["terminal_decisions_added"] == deferred["new_review_actions_added"] == 0


def test_terminal_upsert_has_no_byte_or_timestamp_churn(tmp_path):
    path = tmp_path / "review_decisions.csv"
    raw = (ROOT / DECISIONS).read_bytes()
    path.write_bytes(raw)
    row = next(row for row in read_review_decisions(path) if row["decision_id"] == DECISION_ID)
    assert upsert_review_decision(row, path=path) == row
    assert path.read_bytes() == raw


def test_exactly_one_atomic_original_action_closes_and_R234_stays_pending():
    before = accounting(csv_records(published_bytes(BASE, DECISIONS)), published_context(BASE)["papers"])
    after = accounting(read_review_decisions(ROOT / DECISIONS), load_context()["papers"])
    assert after == packet()["batch_b_accounting"]
    fields = ("historical_actions", "historical_papers", "historical_unresolved_actions", "historical_unresolved_papers", "active_public_unresolved_actions", "active_public_unresolved_papers")
    assert [before[key] for key in fields] == [159, 148, 138, 128, 136, 126]
    assert [after[key] for key in fields] == [159, 148, 137, 127, 135, 125]
    assert set(after["closed_review_ids"]) - set(before["closed_review_ids"]) == {"R596"}
    for name in ("historical_unresolved_review_ids", "active_public_unresolved_review_ids"):
        assert after[name] == [rid for rid in before[name] if rid != "R596"]
        assert "R234" in after[name]
    ledger = [row for row in decision_rows(load_queues()) if row["batch"] == "B"]
    assert {row["review_id"] for row in ledger if row["paper_id"] == TARGET} == {"R596"}
    assert {row["review_id"] for row in ledger if row["paper_id"] == DEFERRED} == {"R234"}


def test_exact_official_18_page_primary_version_and_unverified_other_version_equivalence():
    source = science("R596")["source"]
    assert source["url"] == "https://www.ecva.net/papers/eccv_2022/papers_ECCV/papers/136740140.pdf"
    assert source["sha256"] == PDF_SHA256 and source["bytes"] == 6642878
    assert source["pages"] == 18 and source["main_pages"] == 14 and source["reference_pages"] == 4
    assert source["full_manuscript_read"] is True and source["pages_read"] == list(range(1, 19))
    assert source["authors"] == ["Tu Bui", "Ning Yu", "John Collomosse"]
    assert source["canonical_publisher_DOI"] == "10.1007/978-3-031-19781-9_9"
    assert source["arxiv_complete_manuscript_obtained"] is source["supplement_obtained"] is source["publication_final_equivalence_verified"] is False


def test_Attribution88_resource_counts_are_base_counts_not_corruption_cross_products():
    p = science("R596")["protocol"]
    assert p["source_label_space"] == ["Real", "ProGAN", "CramerGAN", "MMDGAN", "SNGAN", "StyleGAN", "StyleGAN2", "StyleGAN3"]
    assert (p["GAN_architecture_families"], p["source_classes"], p["semantic_classes"]) == (7, 8, 11)
    assert p["source_semantic_cells"] == 88 and p["final_per_source_semantic_cell"] == 12000
    assert p["final_base_images_derived"] == 1056000 == 8 * 11 * 12000
    assert p["final_real_images_derived"] == 132000 and p["final_synthetic_images_derived"] == 924000
    assert p["per_cell_train_validation_test"] == [10000, 1000, 1000]
    assert p["all11_base_partitions_derived"] == [880000, 88000, 88000]
    assert p["all95_type_severity_realizations_per_image_verified"] is p["actual_processed_test_image_count_verified"] is False


def test_semantic_holdouts_do_not_become_unknown_architecture_open_set_attribution():
    p = science("R596")["protocol"]
    assert p["semantic_seen"] == ["CelebA Face", "Bedroom", "Airplane", "Classroom", "Cow", "Church Outdoor"]
    assert p["semantic_held_out"] == ["Bridge", "Bus", "Sheep", "Kitchen", "Cat"]
    assert p["intended_GAN_instances"] == 77
    assert p["intended_training_GAN_instances_derived"] == 42 and p["intended_held_out_semantic_GAN_instances_derived"] == 35
    assert p["closed_set"] is True and p["unknown_architecture_open_set_evaluated"] is False
    assert p["architecture_labels_held_out"] == 0 and p["instance_and_semantic_shift_independently_isolated"] is False
    assert p["actual_validation_semantic_membership_verified"] is False and p["conditional_validation_count_is_not_observed"] is True
    assert record(packet(), "R596")["root_clarification"] == record(original(), "R596")["root_clarification"]
    assert "must not be read as a held-out-architecture protocol" in record(packet(), "R596")["root_clarification"]["clarification"]


def test_corruptions_severities_and_held_out_types_have_exact_definitions():
    p = science("R596")["protocol"]
    assert p["corruption_types"] == 19 and p["severity_levels"] == [1, 2, 3, 4, 5]
    assert p["seen_corruption_types"] == 15
    assert p["held_out_corruption_types"] == ["Glass blur", "Motion blur", "Zoom blur", "Snow"]
    assert p["held_out_corruption_IDs_in_pinned_code"] == [4, 5, 6, 7]
    assert p["train_recipe_from_paper"]["seen_corruption_activation_probability"] == 0.95
    assert "20 iterations" in p["adversarial_protocol"] and "before-minus-after" in p["adversarial_protocol"]


def test_all_142_source_located_numeric_values_and_source_lines_remain_exact():
    numerical = science("R596")["quantitative_tables"]
    raw = json.dumps(numerical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    assert digest(raw) == QUANTITATIVE_SHA256
    tables = numerical["tables"]
    assert [t["table"] for t in tables] == [1, 2, 3] and [t["PDF_page"] for t in tables] == [8, 10, 11]
    assert [len(t["rows"]) for t in tables] == [7, 3, 7]
    assert sum(len(r["values"]) for t in tables for r in t["rows"]) == numerical["table_numeric_cells"] == 81
    assert all(r["source_line"] for t in tables for r in t["rows"])
    f3, f7 = (numerical["additional_printed_figure_values"][n] for n in ("Figure 3", "Figure 7"))
    assert len(f3["rows"]) == 19 and len(f7["values"]) == 4
    assert sum(len(r["values"]) for r in f3["rows"]) + len(f7["values"]) == numerical["additional_printed_figure_numeric_cells"] == 61
    assert science("R596")["quantitative_scalar_values_transcribed"] == 81 + 61 == 142


def test_main_accuracy_NMI_and_binary_class_imbalance_remain_distinct():
    review = science("R596")
    rows = {row["method"]: row["values"] for row in review["quantitative_tables"]["tables"][0]["rows"]}
    assert rows["RepMix"][3:] == ["0.9745", "0.8207", "0.6679"]
    assert rows["Yu et al. reimplementation"][3:] == ["0.9306", "0.6784", "0.4666"]
    assert rows["RepMix"][:3] == ["1.0000", "0.9994", "0.9975"]
    p = review["protocol"]
    assert p["detection_metric"] == "Raw binary real-versus-non-real accuracy, not balanced accuracy."
    assert p["attribution_metric"] == "Eight-class source accuracy including Real."
    assert "normalized_mutual_info_score" in p["NMI_metric"] and "including Real" in p["NMI_metric"]
    assert p["nominal_binary_real_fake_ratio"] == [1, 7] and p["always_fake_detection_accuracy_derived"] == 0.875


def test_nonuniform_performance_and_coupled_generalization_counterexamples_are_retained():
    review = science("R596")
    figures = review["quantitative_tables"]["additional_printed_figure_values"]
    glass = next(row for row in figures["Figure 3"]["rows"] if row["perturbation"] == "Glass blur")
    assert glass["values"] == ["0.67", "0.77", "0.24"] and glass["held_out_type"] is True
    assert figures["Figure 7"]["values"] == {"seen_semantic_seen_transform": "0.9377", "seen_semantic_unseen_transform": "0.8405", "unseen_semantic_seen_transform": "0.7192", "unseen_semantic_unseen_transform": "0.6505"}
    ablation = {row["method"]: row["values"] for row in review["quantitative_tables"]["tables"][2]["rows"]}
    assert ablation["VGG16"] == ["0.9493", "0.7150", "0.5315"] and ablation["All components"] == ["0.9426", "0.7400", "0.5546"]
    assert ablation["Without augmentation"][0] == "0.7044"
    results = review["key_numerical_results"]
    assert results["adversarial_epsilon32_drops"] == ["0.3572", "0.4534", "0.3812"]
    assert results["adversarial_epsilon32_final_accuracy_percent_prose"] == [46.35, 22.49, 26.34]
    assert results["adversarial_epsilon32_baseline_minus_drop_percent_derived"] == [46.35, 22.5, 26.35]
    assert len(review["counterevidence_and_limits"]) == 8


def test_R2_eligibility_is_independent_protocol_not_scale_or_required_download_availability():
    review = science("R596")
    a = review["policy_assessment"]
    assert a["locked_R2"]["policy_id"] == "R2"
    assert all(term in a["positive_R2_basis"] for term in ("fixed architecture-level source classes", "fixed per-cell base partitions", "held-out semantics", "independent accuracy/NMI metrics", "Another classifier"))
    assert "word benchmark, scale and number of sources alone would not suffice" in a["competing_interpretation"]
    assert "not imposed as the sole or mandatory condition" in a["threshold_reasoning"]
    assert a["contribution_confidence"] == "high" and a["reproduction_confidence"] == "medium"
    assert review["protocol"]["independent_baseline_families"] == ["Yu et al.", "DCT-CNN", "Reverse Engineering", "EigenFace", "PRNU"]
    assert review["protocol"]["independent_baseline_rows"] == 6
    assert review["provisional_outcome"] == "BENCHMARK_ADDITION_SUPPORTED"


def test_pinned_release_advertisements_do_not_become_complete_asset_or_upstream_rights_verification():
    r = science("R596")["release_review"]
    assert r["pinned_commit"] == CODE_COMMIT and "CC BY 4.0" in r["repository_license_declared"]
    assert len(r["archive_advertisements"]) == 2 and all(not row["requested"] for row in r["archive_advertisements"])
    assert r["dataset_archive_license_independently_verified"] is r["underlying_LSUN_CelebA_rights_independently_verified"] is False
    assert r["complete_dataset_release_verified"] is r["split_CSV_payloads_obtained"] is r["author_code_executed"] is False
    assert r["dataset_image_or_archive_bytes_downloaded"] == 0 and r["standalone_split_CSVs_in_fetched_tree"] == []
    assert r["split_CSV_interface"]["required_fields"] == ["path", "label", "dlabel"]
    assert len(r["code_files_passively_inspected"]) == 8 and all(not row["executed"] for row in r["code_files_passively_inspected"])
    assert "val_total_loss_epoch" in science("R596")["protocol"]["paper_code_early_stop_difference"]
    assert science("R596")["protocol"]["numerical_reproduction_completed"] is False


def test_R234_original_atomic_R1_R2_question_and_current_taxonomy_remain_unmodified():
    row = record(packet(), "R234")
    assert row == record(original(), "R234")
    review = row["scientific_review"]
    for path in (PAPERS, TAXONOMY):
        assert selected_row((ROOT / path).read_bytes(), DEFERRED) == selected_row(published_bytes(BASE, path), DEFERRED)
    assert load_context()["papers"][DEFERRED] == published_context(BASE)["papers"][DEFERRED]
    assert review["proposed_complete_research_types"] == review["current_research_types"] == ["method"]
    assert review["proposed_tasks"] == ["detection"] and review["proposed_image_scopes"] == ["fully_generated"]
    assert review["dataset_evidence_conclusion"]["outcome"] == review["benchmark_evidence_conclusion"]["outcome"] == "EVIDENCE_STILL_INSUFFICIENT"
    assert review["provisional_outcome"] == "EVIDENCE_STILL_INSUFFICIENT" and review["evidence_scientifically_sufficient"] is False
    assert "NOTSUPPORTED_NO_CHANGE" in review["proposal_meaning"]
    assert row["maintainer_acceptance_pending"] is True
    assert row["review_closed"] is row["authoritative_changes_applied"] is row["terminal_review_decision_created"] is False
    assert len(review["question_matrix"]) == 20 and all(not item["scientifically_sufficient"] for item in review["question_matrix"])


def test_R234_access_failures_and_DiffuGen_metadata_claims_are_not_promoted_to_primary_science():
    review = science("R234")
    s = review["source"]
    assert s["complete_manuscript_obtained"] is s["full_manuscript_read"] is False
    assert s["url"] is s["sha256"] is s["version"] is s["pages"] is None and s["bytes"] == 0 and s["pages_read"] == []
    assert all(term in s["access_blocker"] for term in ("HTTP202/0B", "TLS", "metadata"))
    assert review["available_evidence"]["abstract_status"] == "UNVERIFIED_ABSTRACT_CLAIM_NOT_COMPLETE_SCIENTIFIC_EVIDENCE"
    assert review["quantitative_tables"] == [] and review["quantitative_evidence"]["verified_primary_table_cells"] == 0
    assert all(not claim["independently_verified"] for claim in review["quantitative_evidence"]["unverified_metadata_claims"])
    assert review["release_and_licensing"]["release_verified"] is review["release_and_licensing"]["license_verified"] is False
    assert review["new_historical_actions_created"] == 0


def test_R234_2025_raw_venue_observation_remains_outside_the_research_type_transaction():
    o = science("R234")["out_of_scope_bibliographic_observation"]
    assert o["marker"] == "OUT_OF_SCOPE_BIBLIOGRAPHIC_OBSERVATION"
    assert o["canonical_year"] == "2026" and o["official_program_year"] == 2026
    assert o["stored_raw_venue"] == "2025 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)"
    assert o["correction_applied"] is o["new_historical_action_created"] is o["complete_manuscript_version_verified"] is False
    before, after = selected_row(published_bytes(BASE, PAPERS), DEFERRED), selected_row((ROOT / PAPERS).read_bytes(), DEFERRED)
    assert before == after and after["year"] == "2026" and after["raw_venue"] == o["stored_raw_venue"]
    assert after["doi"] == "10.1109/icassp55912.2026.11462468"


def test_original_one_manuscript_and_zero_adjudication_downloads_are_honest():
    r = packet()["retrieval_accounting"]
    assert r == original()["retrieval_accounting"]
    assert r["new_complete_manuscripts_by_review"] == {"R596": 1, "R234": 0} and r["new_complete_manuscripts_total"] == 1
    assert r["supplements_downloaded"] == r["datasets_or_image_archives_downloaded"] == r["model_weights_downloaded"] == r["repository_clones_or_archives_downloaded"] == 0
    assert packet()["adjudication"]["scientific_source_retrievals_during_adjudication"] == 0


def test_exact_one_public_paper_and_actual_existing_dependents_change_only_types_and_reason():
    old, live = published_context(BASE), load_context()
    assert old["papers"].keys() == live["papers"].keys() and len(live["papers"]) == 674
    assert {pid for pid in old["papers"] if old["papers"][pid] != live["papers"][pid]} == {TARGET}
    assert sum(old["papers"][pid] == live["papers"][pid] for pid in old["papers"] if pid != TARGET) == 673
    expected = deepcopy(old["papers"][TARGET])
    expected["research_types"] = FINAL_TYPES
    expected["taxonomy_review"]["research_types"]["reason"] = CSV_UPDATES[TAXONOMY]["research_types_review_reason"]
    assert live["papers"][TARGET] == expected
    assert old["pairs"] == live["pairs"] and sum(live["pairs"].values()) == len(live["pairs"]) == 1410
    for path in PUBLIC:
        before, after = json.loads(published_bytes(BASE, path)), json.loads((ROOT / path).read_bytes())
        oldmeta, newmeta = deepcopy(before["metadata"]), deepcopy(after["metadata"])
        oldmeta.pop("public_preview_generated_at", None); newmeta.pop("public_preview_generated_at", None)
        assert oldmeta == newmeta
        assert {k: v for k, v in before.items() if k not in {"records", "metadata"}} == {k: v for k, v in after.items() if k not in {"records", "metadata"}}
    before = {row["id"]: row for row in json.loads(published_bytes(BASE, PUBLIC[1]))["records"]}
    after = {row["id"]: row for row in json.loads((ROOT / PUBLIC[1]).read_bytes())["records"]}
    assert before.keys() == after.keys() and len(after) == 1410
    dependents = {key for key, row in before.items() if row.get("paper_id") == TARGET}
    assert dependents and {key for key in before if before[key] != after[key]} == dependents
    assert len(dependents) == 3
    for key, row in before.items():
        expected = deepcopy(row)
        if key in dependents:
            expected["research_types"] = FINAL_TYPES
            expected["taxonomy_review"]["research_types"]["reason"] = CSV_UPDATES[TAXONOMY]["research_types_review_reason"]
        assert after[key] == expected, key
    semantic = packet()["semantic_delta"]
    assert semantic["status"] == "PASS" and semantic["dependent_R596_map_records"] == len(dependents)
    assert set(semantic["dependent_R596_map_record_ids"]) == dependents
    assert semantic["all_relationship_identities_unchanged"] is semantic["R234_public_and_map_records_unchanged"] is True


def test_recomputed_corpus_tasks_scopes_and_types_add_exactly_one_benchmark():
    old, live = published_context(BASE), load_context()
    assert old["counts"] == live["counts"] == packet()["corpus_counts"] == CURRENT_CORPUS_COUNTS
    def totals(c):
        return Counter(label for row in c["papers"].values() for dimension in ("tasks", "research_types") for label in row[dimension])
    before, after = totals(old), totals(live)
    assert not before - after and after - before == {"benchmark": 1}
    assert before["benchmark"] == 93 and after["benchmark"] == 94
    assert after == packet()["taxonomy_counts"] == CURRENT_TAXONOMY_TOTALS
    assert after == {"detection": 621, "source_attribution": 84, "localization": 45, "method": 578, "dataset": 137, "benchmark": 94, "survey": 21, "analysis_study": 82}
    assert {pid: row["image_scopes"] for pid, row in old["papers"].items()} == {pid: row["image_scopes"] for pid, row in live["papers"].items()}


def test_original_questions_policies_and_unrelated_authoritative_files_are_unchanged():
    rows = {row["review_id"]: row for row in load_queues()["taxonomy_review"]["records"]}
    for rid in ("R596", "R234"):
        assert record(packet(), rid)["original_review"] == rows[rid]
    policies = json.loads((ROOT / (AUDIT + "batch_c_policy_decisions.json")).read_bytes())["policies"]
    locked = {row["policy_id"]: row for row in policies}
    assert science("R596")["policy_assessment"]["locked_R2"] == locked["R2"]
    assert science("R234")["locked_policies"] == {key: locked[key] for key in ("R1", "R2")}
    allowed = {PAPERS, TAXONOMY, DECISIONS, *PUBLIC}
    for path in baseline_paths("data/curated", "data/manual", "web/data"):
        if path not in allowed:
            assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path
    for name in ("taxonomy_review", "publication_metadata_review", "relationship_review", "unmapped_papers", "batch_c_policy_decisions"):
        path = AUDIT + name + ".json"
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_current_authority_fingerprints_change_only_five_allowed_data_dependencies():
    old, new = original(), packet()
    assert new["source_files_sha256"] == old["source_files_sha256"]
    current = new["current_source_sha256"]
    assert current.keys() == old["source_files_sha256"].keys()
    assert {p for p in current if current[p] != old["source_files_sha256"][p]} == {PAPERS, TAXONOMY, DECISIONS, *PUBLIC}
    tracked = set(baseline_paths())
    fixtures = {row["path"]: row for row in json.loads(published_bytes(BASE, FIXTURES))["entries"]}
    for path, expected in current.items():
        if path in tracked:
            raw = (ROOT / path).read_bytes()
        elif path in fixtures:
            entry = fixtures[path]
            assert entry["compression"] == "none"
            raw = published_bytes(BASE, entry["source"])
            assert len(raw) == entry["bytes"] and digest(raw) == entry["sha256"] == entry["source_sha256"]
        else:
            raw = preserved_bytes(ROOT, path)
            preflight = json.loads(published_bytes(BASE, "data/processed/literature51_2026_10_16/followup/commit_preflight.json"))
            authority = preflight["reproduction_inputs"][path]
            assert len(raw) == authority["bytes"] and digest(raw) == authority["original_sha256"] == old["source_files_sha256"][path]
        assert digest(raw) == expected, path


def test_prior_26_packets_fixtures_frozen49_C13_and_separate39_remain_immutable():
    prior = original()["prior_B1A_M_artifact_sha256"]
    assert len(prior) == 26
    for path, expected in prior.items():
        assert digest(published_bytes(BASE, path)) == digest((ROOT / path).read_bytes()) == expected, path
    for path in baseline_paths("tests/fixtures"):
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path
    migration = "data/raw/systematic_gap_migration_2026_10_03/baseline.json"
    raw = (ROOT / migration).read_bytes()
    assert raw == published_bytes(BASE, migration)
    frozen = json.loads(raw)["frozen_sha256"]
    assert len(frozen) == 49
    for path, expected in frozen.items():
        assert digest(preserved_bytes(ROOT, path)) == expected, path
    assert packet()["neurips_status"] == "7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA"
    debt = packet()["batch_c_deferred_accounting"]
    assert debt == original()["batch_c_deferred_accounting"]
    assert debt["total_actions"] == 41 and debt["resolved"] == 28
    assert debt["total_unresolved"] == debt["external_unresolved"] == len(debt["remaining_external_ids"]) == 13
    assert debt["maintainer_judgments"] == 0
    intake = packet()["separate_import_review_inventory"]
    assert intake == original()["separate_import_review_inventory"]
    assert intake["imported_papers"] == intake["unmapped"] == len(intake["candidate_to_paper"]) == 39
    assert intake["relationships"] == 0 and intake["taxonomy_pending"] == 14 and intake["held"] == 12
    for pid in intake["candidate_to_paper"].values():
        assert load_context()["papers"][pid] == published_context(BASE)["papers"][pid]


def test_original_43_preservation_36_packet_120_science_42_provenance_receipts_remain_separate():
    entries = packet()["evidence_stage_preservation_receipts"]
    for name, count, expected in (
        ("integrity-final.json", 43, "06d0620b25e5bf931b695f503d2b80e8bab035529971796b4ad13d4dd519ee2d"),
        ("packet-validation-final.json", 36, "373bb3303104509b0565572d81af51515c3a65d0af09853ecddaef9208a6182a"),
        ("independent-scientific-crossreview.json", 120, "e6e92684e1b8ed3bbc6e43fc93ace274fbe05a9e893f3570ce817160de7de6ef"),
        ("independent-source-provenance.json", 42, "f0cc4047470731b1f1b98ecf430cddfd3fb502d528283ed1b0b72bf394395869"),
    ):
        entry = entries[name]
        assert digest(decode_archive(entry)) == expected
        receipt = json.loads(decode_archive(entry))
        assert receipt == entry["receipt"] and receipt["passed"] == count and receipt["failed"] == 0
        assert all(check["passed"] for check in receipt["checks"])


def test_report_keeps_complete_original_history_and_separate_accepted_and_deferred_dispositions():
    report = (ROOT / REPORT).read_text()
    assert archived_bytes("report").decode() in report
    for token in (DECISION_ID, "R596", "R234", "PROPOSE_CORRECTION_ACCEPTED", "method;dataset;benchmark", "EVIDENCE_STILL_INSUFFICIENT", "OUT_OF_SCOPE_BIBLIOGRAPHIC_OBSERVATION", "0.9745", "0.8207", "0.6679", "0.9306", "0.6784", "0.4666", BASE):
        assert token in report
    assert packet()["scope"]["review_decisions_added"] == packet()["scope"]["review_actions_closed"] == 1
    for key in ("forensic_task_changes", "image_scope_changes", "publication_metadata_changes", "new_Batch_B_actions_added", "Batch_B_denominator_changes"):
        assert packet()["scope"][key] == 0
