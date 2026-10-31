"""B1J adds two independently accepted resource roles without task changes."""
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
BASE = "1221cf72f8f77ac3430cad49a49d074d82b36ec2"
# The completed B1J transaction is historical; selected accepted rows remain live guards.
PUBLISHED = "b2f17505f2d3a1b65d43fcf3c6582436b4fe44f8"
PAPERS = "data/curated/papers.csv"
TAXONOMY = "data/curated/paper_taxonomy.csv"
DECISIONS = "data/curated/review_decisions.csv"
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1j_2026_10_21/evidence_manifest.json"
REPORT = "docs/corpus_quality_batch_b_wave_b1j_2026_10_21.md"
AUDIT = "data/raw/corpus_quality_audit_2026_10_04/"
FIXTURES = "tests/fixtures/historical_test_fixture_manifest.json"
TARGETS = {"R100": "curated:411724cd949b78c1af6a", "R400": "curated:b2fccf1dd66cc2d64374"}
IDS = {"R100": "review:926fcbf72f575cdf407a", "R400": "review:e603cf0e2cfc1e986aec"}
FINAL_TYPES = {"R100": ["method", "dataset"], "R400": ["method", "dataset", "benchmark"]}
EVIDENCE_HASHES = {
    "manifest": "eb2c49f2485e5c76f6e2d35a3f8f7877acbbb61a5fc0c4ab81f35a8e6867d563",
    "report": "6d9b802b7decdb2c1cb60d7512cbba0269305ecaa4750ecced6c7625f9620be9",
}
WORKER_HASHES = {
    "R100": "295e98ee000cd1517cc658c879dc695a912f699ff0c544f1bb4a0ae0bbe6b203",
    "R400": "46253952695d12be5b7323123ece96738392017ce8aa34cfd655312615e5d2a9",
}
PDF_HASHES = {
    "R100": "dc58c87cd13f7ad52102cc6f6b9c5f95f35a7ae24c0c1629bc39de01ad38aed9",
    "R400": "6fab4d3e07ea14ea2c111f4c5b87635bc5c587d485e2fb6e73b380bd0e5bab70",
}
# Filled from the independently reviewed row/token plan, not an operational cache.
CSV_UPDATES = {'data/curated/papers.csv': {'R100': {'research_types': 'method;dataset'},
                             'R400': {'research_types': 'method;dataset;benchmark'}},
 'data/curated/paper_taxonomy.csv': {'R100': {'research_types': 'method;dataset',
                                              'research_types_review_reason': 'R100 accepted under '
                                                                              'locked R1: the '
                                                                              'complete official '
                                                                              'ICLR 2026 '
                                                                              'conference '
                                                                              'manuscript '
                                                                              'establishes '
                                                                              'FakeXplained as a '
                                                                              'substantive '
                                                                              'original reusable '
                                                                              'annotated resource '
                                                                              'independently of '
                                                                              'FakeXplainer, with '
                                                                              '8,772 images, 23 '
                                                                              'trained annotators, '
                                                                              'region-caption '
                                                                              'pairs, six tags, '
                                                                              'documented quality '
                                                                              'control and '
                                                                              'resource-related '
                                                                              'experiments. Add '
                                                                              'dataset; retain '
                                                                              'method and '
                                                                              'detection. The '
                                                                              'text/Table 1 '
                                                                              'generator count '
                                                                              'differs (28/27), '
                                                                              'MLLM annotation '
                                                                              'assistance is '
                                                                              'incompletely '
                                                                              'quantified, '
                                                                              'annotation has '
                                                                              'subjective '
                                                                              'components, and '
                                                                              'public assets, '
                                                                              'official '
                                                                              'partitions, '
                                                                              'license, download '
                                                                              'completeness and '
                                                                              'numerical '
                                                                              'reproduction are '
                                                                              'unverified; the '
                                                                              'author repository '
                                                                              'was empty at '
                                                                              'inspection. Public '
                                                                              'availability is not '
                                                                              'the sole R1 '
                                                                              'criterion. The '
                                                                              'separate '
                                                                              'artifact-localization '
                                                                              'observation is '
                                                                              'preserved for '
                                                                              'future authorized '
                                                                              'T2 review only; no '
                                                                              'task or '
                                                                              'review-action '
                                                                              'addition is '
                                                                              'applied.',
                                              'research_types_evidence_tier': 'primary_paper',
                                              'research_types_evidence_source': 'https://proceedings.iclr.cc/paper_files/paper/2026/file/701ec28790b29a5bc33832b7bdc4c3b6-Paper-Conference.pdf',
                                              'research_types_evidence_excerpt': 'Official ICLR '
                                                                                 '2026 paper: '
                                                                                 'FakeXplained has '
                                                                                 '8,772 annotated '
                                                                                 'images, 23 '
                                                                                 'trained '
                                                                                 'annotators, '
                                                                                 'average 5.42 '
                                                                                 'region-caption '
                                                                                 'pairs and six '
                                                                                 'global tags. '
                                                                                 'Annotation '
                                                                                 'quality control '
                                                                                 'covers 5%; final '
                                                                                 'reference IoU '
                                                                                 '42.35% and tag '
                                                                                 'agreement '
                                                                                 '79.67%. Resource '
                                                                                 'construction, '
                                                                                 'annotation-related '
                                                                                 'experiments and '
                                                                                 'use by other '
                                                                                 'detection '
                                                                                 'methods support '
                                                                                 'dataset '
                                                                                 'independently of '
                                                                                 'FakeXplainer. '
                                                                                 'Text claims 28 '
                                                                                 'generators, '
                                                                                 'Table 1 lists '
                                                                                 '27; MLLM '
                                                                                 'assistance, '
                                                                                 'subjectivity, '
                                                                                 'empty author '
                                                                                 'repository, '
                                                                                 'public assets, '
                                                                                 'official '
                                                                                 'partitions and '
                                                                                 'licensing remain '
                                                                                 'bounded '
                                                                                 'uncertainties. '
                                                                                 'Reported 98.2% '
                                                                                 'detection and '
                                                                                 '36.0% artifact '
                                                                                 'IoU do not '
                                                                                 'authorize a task '
                                                                                 'change here.',
                                              'audited_at': '2026-10-21'},
                                     'R400': {'research_types': 'method;dataset;benchmark',
                                              'research_types_review_reason': 'R400 accepted under '
                                                                              'locked R2: the '
                                                                              'complete official '
                                                                              'CVF CVPR 2025 Main '
                                                                              'paper defines '
                                                                              'FakeART as a '
                                                                              'reusable '
                                                                              'photo-to-art '
                                                                              'evaluation '
                                                                              'task/protocol '
                                                                              'independently of '
                                                                              'CoD, with COCO/LSUN '
                                                                              'sources, '
                                                                              'SD1.4/ProGAN '
                                                                              'training, 7,000 '
                                                                              'WikiArt real test '
                                                                              'artworks, seven '
                                                                              'test-model '
                                                                              'variants, ACC '
                                                                              'threshold 0.5 and '
                                                                              'ACC/AP comparisons. '
                                                                              'Add benchmark; '
                                                                              'retain method, '
                                                                              'dataset and '
                                                                              'detection. This is '
                                                                              'a medium-confidence '
                                                                              'contribution-based '
                                                                              'framework judgment, '
                                                                              'not numerical '
                                                                              'reproduction. '
                                                                              'Synthetic counts, '
                                                                              'class balance, '
                                                                              'exact splits, '
                                                                              'identical baseline '
                                                                              'retraining, '
                                                                              'evaluation code, '
                                                                              'complete release '
                                                                              'and licensing are '
                                                                              'unverified; '
                                                                              'style/content/generator '
                                                                              'shifts are '
                                                                              'confounded. Prior '
                                                                              'training-count, '
                                                                              'GAN-score and '
                                                                              'AP-aggregation '
                                                                              'discrepancies '
                                                                              'remain documented. '
                                                                              'No mandatory '
                                                                              'new-code criterion '
                                                                              'is introduced.',
                                              'research_types_evidence_tier': 'primary_paper',
                                              'research_types_evidence_source': 'https://openaccess.thecvf.com/content/CVPR2025/papers/Jia_Secret_Lies_in_Color_Enhancing_AI-Generated_Images_Detection_with_Color_CVPR_2025_paper.pdf',
                                              'research_types_evidence_excerpt': 'Sections '
                                                                                 '4.1.2-4.1.3 and '
                                                                                 'Figure 5 define '
                                                                                 'photo-training '
                                                                                 'to '
                                                                                 'artwork-testing '
                                                                                 'FakeART: 50,000 '
                                                                                 'COCO/LSUN source '
                                                                                 'images, '
                                                                                 'SD1.4/ProGAN '
                                                                                 'train '
                                                                                 'generators, '
                                                                                 '7,000 real '
                                                                                 'WikiArt artworks '
                                                                                 'and seven '
                                                                                 'held-out '
                                                                                 'diffusion test '
                                                                                 'variants. ACC '
                                                                                 'threshold 0.5; '
                                                                                 'Table 4 CoD '
                                                                                 'ACC/AP 66.5/68.2 '
                                                                                 'versus '
                                                                                 'PatchCraft '
                                                                                 '58.7/59.5. The '
                                                                                 'transferable '
                                                                                 'evaluation '
                                                                                 'framework '
                                                                                 'supports '
                                                                                 'benchmark '
                                                                                 'independently of '
                                                                                 'CoD. Synthetic '
                                                                                 'counts, balance, '
                                                                                 'exact splits, '
                                                                                 'identical '
                                                                                 'baseline '
                                                                                 'conditions, full '
                                                                                 'release, license '
                                                                                 'and numerical '
                                                                                 'reproduction are '
                                                                                 'unverified; '
                                                                                 'joint shifts and '
                                                                                 'training-count/GAN-score/AP-aggregation '
                                                                                 'discrepancies '
                                                                                 'remain explicit.',
                                              'audited_at': '2026-10-21'}}}
CSV_AFTER_HASHES = {'data/curated/papers.csv': 'b367c07b3238b05188ac255b181c29999647aebb09d0dc11d8334559327a74bf',
 'data/curated/paper_taxonomy.csv': 'fa45db0cdb96706f6c911ab8097b6d83a711014ca48fee1aa599ca0fd05020cd'}


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
    rows = [row for row in data["records"] if row["review_id"] == review_id]
    assert len(rows) == 1
    return rows[0]


def selected_row(raw, paper_id):
    rows = [row for row in csv_records(raw) if row["paper_id"] == paper_id]
    assert len(rows) == 1
    return rows[0]


def terminal(rows):
    result = {}
    for row in rows:
        match = re.search(r"\bBatch B review ([A-Z]\d{3});", row["review_note"])
        if match and row["action"] == "no_action_after_review":
            assert match[1] not in result, "Duplicate terminal decision for an original action"
            result[match[1]] = row["decision_id"]
    return result


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
    """Construct expected cells while preserving every other source token."""
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
    ledger = [row for row in decision_rows(load_queues()) if row["batch"] == "B"]
    done = terminal(rows)
    pending = [row for row in ledger if row["review_id"] not in done]
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
def test_complete_evidence_only_packet_is_portable_and_hash_exact(kind):
    assert archived_bytes(kind)
    assert set(packet()["evidence_only_packet_archives"]) == {"manifest", "report"}
    validation = original()["validation"]
    assert validation["status"] == "PASS"
    for key in ("recovered_draft_validation", "final_path_lightweight_evidence_checks"):
        assert validation[key]["status"] == "PASS"
        assert validation[key]["passed"] == 44 and validation[key]["failed"] == 0
    assert validation["independent_preservation_checks"]["passed"] == 34
    assert validation["independent_preservation_checks"]["failed"] == 0
    assert validation["independent_checks_passed"] == {
        "R100": 32, "R400_cross_review": 41, "R400_second_review": 31}


@pytest.mark.parametrize("path", [PAPERS, TAXONOMY])
def test_exact_two_rows_fourteen_cells_and_every_unapproved_csv_token_survive(path):
    before_raw, after_raw = published_bytes(BASE, path), published_bytes(PUBLISHED, path)
    before, after = csv_records(before_raw), csv_records(after_raw)
    identity = "taxonomy_id" if path == TAXONOMY else "paper_id"
    assert len(before) == len(after)
    assert [row[identity] for row in before] == [row[identity] for row in after]
    assert len({row[identity] for row in after}) == len(after)
    assert {old["paper_id"] for old, new in zip(before, after) if old != new} == set(TARGETS.values())
    for rid, paper_id in TARGETS.items():
        old, new = selected_row(before_raw, paper_id), selected_row(after_raw, paper_id)
        updates = CSV_UPDATES[path][rid]
        assert {key for key in old if old[key] != new[key]} == updates.keys()
        assert new == {**old, **updates}
        assert new["research_types"] == ";".join(FINAL_TYPES[rid])
        assert new["tasks"] == "detection" and new["image_scopes"] == "fully_generated"
        if path == TAXONOMY:
            assert new["research_types_status"] == old["research_types_status"] == "reviewed"
            assert new["research_types_evidence_tier"] == "primary_paper"
            assert new["audited_at"] == "2026-10-21"
            assert new["research_types_evidence_source"] == record(original(), rid)["scientific_review"]["source"]["url"]
    chunks = logical_csv_chunks(before_raw)
    header = next(csv.reader(io.StringIO(before_raw.decode(), newline="")))
    target_to_review = {pid: rid for rid, pid in TARGETS.items()}
    expected = [chunks[0]]
    for old, chunk in zip(before, chunks[1:]):
        rid = target_to_review.get(old["paper_id"])
        expected.append(replace_csv_tokens(chunk, header, CSV_UPDATES[path][rid]) if rid else chunk)
    assert after_raw == b"".join(expected)
    assert digest(after_raw) == CSV_AFTER_HASHES[path]


def test_two_terminal_appends_preserve_all_89_prior_rows_and_registry_bytes():
    before, after = published_bytes(BASE, DECISIONS), published_bytes(PUBLISHED, DECISIONS)
    old, rows = csv_records(before), csv_records(after)
    assert after.startswith(before)
    assert len(old) == 89 and len(rows) == 91
    assert rows[:-2] == old
    assert len({row["decision_id"] for row in rows}) == len(rows)
    assert terminal(rows) == {**terminal(old), **IDS}
    assert [row["decision_id"] for row in rows[-2:]] == list(IDS.values())
    for rid, row in zip(TARGETS, rows[-2:]):
        assert row["review_queue"] == "other" and row["review_queue"] in ALLOWED_REVIEW_QUEUES
        assert row["target_type"] == "paper" and row["institution"] == ""
        assert row["action"] == "no_action_after_review" and row["action"] in ALLOWED_REVIEW_ACTIONS
        assert row["created_by"] == "maintainer-approved-batch-b-b1j"
        assert row["created_at"] == row["updated_at"]
        assert row["created_at"].startswith("2026-10-21T")
        assert datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")).tzinfo == timezone.utc
        prior = selected_row(published_bytes(BASE, PAPERS), TARGETS[rid])
        for key in ("title", "year", "doi", "openalex_url"):
            assert row[key] == prior[key]
        identity = "|".join(" ".join(row[key].split()).casefold() for key in
                            ("review_queue", "target_type", "doi", "openalex_url", "title", "year", "institution"))
        assert "review:" + digest(identity.encode())[:20] == IDS[rid]
        assert row["review_note"].startswith("Batch B review " + rid + ";")
        assert "PROPOSE_CORRECTION_ACCEPTED" in row["review_note"]
        assert PDF_HASHES[rid] in row["review_note"]
        assert packet()["adjudication"]["terminal_decisions"][rid] == row
    adjudication = packet()["adjudication"]
    assert adjudication["decision_ids"] == IDS
    assert adjudication["registry_rows_before"] == 89 and adjudication["registry_rows_after"] == 91
    assert adjudication["prior_decision_bytes_preserved"] is True
    assert adjudication["before_registry_sha256"] == digest(before)
    assert adjudication["after_registry_sha256"] == digest(after)
    assert adjudication["existing_csv_cells_changed"] == 14
    changes = adjudication["csv_changes"]
    assert len(changes) == 4
    assert {(c["path"], c["row_identity"]["paper_id"]) for c in changes} == {
        (path, paper_id) for path in (PAPERS, TAXONOMY) for paper_id in TARGETS.values()}
    by_paper = {pid: rid for rid, pid in TARGETS.items()}
    for change in changes:
        path, rid = change["path"], by_paper[change["row_identity"]["paper_id"]]
        assert change["after_fields"] == CSV_UPDATES[path][rid]
        assert change["planned_after_sha256"] == CSV_AFTER_HASHES[path]


@pytest.mark.parametrize("rid", ["R100", "R400"])
def test_terminal_upsert_is_idempotent_without_timestamp_or_byte_churn(tmp_path, rid):
    path = tmp_path / "review_decisions.csv"
    raw = (ROOT / DECISIONS).read_bytes()
    path.write_bytes(raw)
    row = next(row for row in read_review_decisions(path) if row["decision_id"] == IDS[rid])
    assert upsert_review_decision(row, path=path) == row
    assert path.read_bytes() == raw


def test_only_two_original_resource_reviews_close_with_derived_distinct_paper_accounting():
    ledger = [row for row in decision_rows(load_queues()) if row["batch"] == "B"]
    before = accounting(csv_records(published_bytes(BASE, DECISIONS)), published_context(BASE)["papers"])
    after = accounting(csv_records(published_bytes(PUBLISHED, DECISIONS)), published_context(PUBLISHED)["papers"])
    assert after == packet()["batch_b_accounting"]
    keys = ("historical_actions", "historical_papers", "historical_unresolved_actions",
            "active_public_unresolved_actions", "active_public_unresolved_papers")
    assert [before[key] for key in keys] == [159, 148, 145, 143, 132]
    assert [after[key] for key in keys] == [159, 148, 143, 141, 130]
    assert before["historical_unresolved_papers"] == 134
    assert after["historical_unresolved_papers"] == 132
    assert set(after["closed_review_ids"]) - set(before["closed_review_ids"]) == set(TARGETS)
    for key in ("historical_unresolved_review_ids", "active_public_unresolved_review_ids"):
        assert after[key] == [rid for rid in before[key] if rid not in TARGETS]
    for rid, pid in TARGETS.items():
        assert [(r["review_id"], r["dimension"]) for r in ledger if r["paper_id"] == pid] == [(rid, "research_types")]
    assert {"R267", "T046", "T093", "T608", "T526", "P526"} <= set(after["active_public_unresolved_review_ids"])
    assert not {"T100", "T400", "P100", "P400"} & terminal(read_review_decisions(ROOT / DECISIONS)).keys()


def test_original_scientific_records_and_retrieval_history_survive_losslessly():
    old, new = original(), packet()
    assert [r["review_id"] for r in new["records"]] == list(TARGETS)
    flags = {"maintainer_acceptance_pending", "review_closed", "authoritative_changes_applied",
             "terminal_review_decision_created"}
    for rid in TARGETS:
        prior, accepted = record(old, rid), record(new, rid)
        for key in prior:
            if key not in flags:
                assert accepted[key] == prior[key], (rid, key)
        assert accepted["scientific_review"] == prior["scientific_review"]
        assert accepted["worker_review_sha256"] == WORKER_HASHES[rid]
        assert accepted["maintainer_acceptance_pending"] is False
        assert accepted["review_closed"] is True
        assert accepted["terminal_review_decision_created"] is True
        assert accepted["authoritative_changes_applied"] is True
        assert accepted["terminal_review_decision_id"] == IDS[rid]
        assert accepted["accepted_outcome"] == "PROPOSE_CORRECTION_ACCEPTED"
        assert accepted["final_authoritative_taxonomy"] == {
            "tasks": ["detection"], "image_scopes": ["fully_generated"], "research_types": FINAL_TYPES[rid]}
    for key in ("retrieval_accounting", "locked_policy_ledger", "source_files_sha256", "prior_B1A_I_artifact_sha256",
                "operational_review_sha256", "preservation", "batch_c_deferred_accounting",
                "separate_import_review_inventory", "root_scientific_spotchecks", "independent_scientific_reviews",
                "evidence_stage_preservation_receipts"):
        assert new[key] == old[key], key
    for key in ("scope", "validation", "integrity", "corpus_counts", "taxonomy_counts", "batch_b_accounting",
                "accounting_effect", "final_git_requirements", "final_git_observation", "phase"):
        assert new["evidence_only_" + key] == old[key], key


def test_R100_substantive_resource_construction_and_annotation_evidence_remain_separate_from_method():
    science = record(packet(), "R100")["scientific_review"]
    assert science["source"]["sha256"] == PDF_HASHES["R100"]
    assert science["source"]["pages"] == 22 and science["source"]["bytes"] == 2117533
    assert science["source"]["full_manuscript_read"] is True
    assert len(science["dataset_review"]) == 15
    assert [r["question_number"] for r in science["dataset_review"]] == list(range(1, 16))
    numbers = science["quantitative_evidence"][0]["numbers"]
    assert numbers == {"annotated_images": 8772, "trained_annotators": 23,
                       "reported_mean_region_caption_pairs": 5.42, "annotation_qc_subset_percent": 5,
                       "minimum_reference_IoU_percent": 20, "minimum_tag_agreement": "1/3",
                       "final_reference_IoU_percent": 42.35, "final_tag_agreement_percent": 79.67}
    assert all(science["contributions"][kind] for kind in ("method", "dataset", "benchmark"))
    assert science["scientific_evidence_sufficient"] is True
    note = packet()["adjudication"]["terminal_decisions"]["R100"]["review_note"]
    for token in ("R1", "8,772", "23", "5.42", "42.35", "79.67", "other detection methods", "sole R1 criterion"):
        assert token in note
    assert "merely" in note and "resource" in note


def test_R100_counterexamples_generator_discrepancy_and_unquantified_MLLM_assistance_are_not_erased():
    science = record(packet(), "R100")["scientific_review"]
    questions = {r["topic"]: r["finding"] for r in science["dataset_review"]}
    assert "28" in questions["generator_models"] and "27" in questions["generator_models"]
    assert "Section H" in questions["manual_vs_automated_stages"]
    assert "not quantified" in questions["manual_vs_automated_stages"]
    counter = science["quantitative_evidence"][2]["contradictory_evidence"]
    assert counter["LlamaGen"] == {"FakeXplainer_IoU": .351, "ObjectFormer_IoU": .429}
    assert counter["GALIP"] == {"FakeXplainer_Acc": .882, "ObjectFormer_Acc": .941, "SegFormer_Acc": .941}
    release = science["release_review"]
    assert release["api_metadata"]["size"] == 0 and release["api_metadata"]["license"] is None
    assert release["api_contents_status"] == 404
    assert release["api_contents_response"]["message"] == "This repository is empty."
    assert release["annotation_files_availability"] == "NOT_VERIFIED_AT_AUTHOR_LINK"
    assert release["data_downloaded"] is False and release["weights_downloaded"] is False
    for token in ("unverified", "empty", "28", "27", "subjective", "MLLM"):
        assert token in CSV_UPDATES[TAXONOMY]["R100"]["research_types_review_reason"]


def test_R100_localization_remains_non_authoritative_and_cannot_close_or_create_task_actions():
    current, old = record(packet(), "R100"), record(original(), "R100")
    observation = current["out_of_scope_task_taxonomy_observation"]
    assert observation == old["out_of_scope_task_taxonomy_observation"]
    assert observation == current["scientific_review"]["out_of_scope_task_taxonomy_observation"]
    assert observation["label"] == "OUT_OF_SCOPE_TASK_TAXONOMY_OBSERVATION"
    assert observation["current_tasks"] == ["detection"]
    assert observation["tasks_changed"] is False
    assert observation["new_Batch_B_actions_added"] == 0
    assert observation["Batch_B_denominators_changed"] is False
    assert observation["future_review_recommendation"] == "YES_SEPARATELY_AUTHORIZED_LOCALIZATION_REVIEW_RECOMMENDED"
    assert "0.360" in observation["metric_and_protocol"]
    assert "not exhaustive" in observation["spatial_ground_truth"]
    assert "not fully specified" in observation["matching_uncertainty"]
    assert load_context()["papers"][TARGETS["R100"]]["tasks"] == ["detection"]
    assert not any(row["review_note"].startswith("Batch B review T100;")
                   for row in read_review_decisions(ROOT / DECISIONS))


def test_R400_protocol_is_reusable_independently_of_CoD_but_not_a_reproducibility_certification():
    science = record(packet(), "R400")["scientific_review"]
    assert science["source"]["sha256"] == PDF_HASHES["R400"]
    assert science["source"]["pages"] == 10 and science["source"]["bytes"] == 8738548
    assert science["source"]["printed_pages"] == "13445–13454"
    assert science["identity_verification"]["doi_normalized"] == "10.1109/cvpr52734.2025.01255"
    assert len(science["identity_verification"]["authors"]) == 10
    assert len(science["question_matrix"]) == 15
    dataset, benchmark = science["dataset_contribution"], science["benchmark_contribution"]
    assert dataset["training_sources"] == ["COCO", "LSUN"]
    assert dataset["training_generators"] == ["ProGAN", "Stable Diffusion v1.4"]
    assert dataset["real_training_source_image_count_stated"] == 50000
    assert dataset["real_test_artwork_count_stated"] == 7000
    assert dataset["test_generators"] == ["SD-1.5", "SD-2.1", "SD-Turbo", "SD-XL", "SD-3", "PlayGround-2.5", "PixArt-α"]
    assert benchmark["contribution_is_separate_from_method"] is True
    assert benchmark["reusable_without_CoD"] is True
    assert benchmark["identical_baseline_training_or_operating_conditions_verified"] is False
    assert benchmark["complete_release_or_execution_reproduction_verified"] is False
    assert science["confidence"].startswith("Medium overall")
    assert "High:" in science["confidence_by_component"]["published_distinct_evaluation_contribution"]
    assert "Not established:" in science["confidence_by_component"]["practical_reproducibility"]


def test_R400_exact_scores_unknown_counts_joint_shifts_and_aggregation_limits_are_preserved():
    science = record(packet(), "R400")["scientific_review"]
    quant = science["quantitative_evidence"]
    table = quant["table4"]
    assert table["rows"]["CoD (Ours)"] == [[76.8, 78.9], [72.1, 73.4], [65.8, 66.2],
        [61.9, 63.4], [61.7, 62.8], [62.3, 64.6], [65.2, 68.1]]
    assert table["reported_means"]["CoD (Ours)"] == [66.5, 68.2]
    assert table["reported_means"]["PatchCraft"] == [58.7, 59.5]
    assert table["CoD_minus_best_other_reported_mean_ACC_percentage_points"] == 7.8
    assert table["CoD_minus_best_other_reported_mean_AP_percentage_points"] == 8.7
    assert [table["reported_means"][name][1] for name in ("CNNDet", "NPR", "SAFE")] == [43.4, 54.6, 58.4]
    assert all(name in table["aggregation_limitation"] for name in ("CNNDet", "NPR", "SAFE"))
    assert quant["conventional_benchmark_reported_means"]["GANs_Table1"] == [98.2, 99.6]
    assert quant["table5_GAN_ACC_Image_Color"] == 98.7
    assert quant["cross_dataset_difference_is_controlled_causal_style_effect"] is False
    dataset = science["dataset_contribution"]
    assert all(dataset[key] is None for key in ("generated_training_count", "generated_test_total", "generated_test_per_model_count"))
    assert dataset["test_class_balance_verified"] is False
    assert dataset["exact_split_ids_or_prompt_registry_verified"] is False
    limitations = " ".join(science["contradictory_evidence_and_limitations"]).casefold()
    for token in ("350,000", "360,000", "98.2", "98.7", "class balance", "license", "split"):
        assert token in limitations
    note = packet()["adjudication"]["terminal_decisions"]["R400"]["review_note"]
    for token in ("R2", "medium-confidence", "0.5", "66.5", "68.2", "58.7", "59.5", "unknown", "unverified", "aggregation"):
        assert token in note


def test_two_original_manuscripts_and_same_ETag_continuation_are_preserved_without_new_retrieval():
    retrieval = packet()["retrieval_accounting"]
    assert retrieval == original()["retrieval_accounting"]
    assert retrieval["new_complete_manuscripts_by_review"] == {"R100": 1, "R400": 1}
    assert retrieval["new_complete_manuscripts_total"] == 2
    assert retrieval["source_or_evaluation_code_executed"] is False
    for key in ("root_new_manuscript_retrievals", "alternate_full_manuscripts", "separate_supplements",
                "dataset_asset_payloads", "model_weight_payloads", "repository_archives"):
        assert retrieval[key] == 0
    r100, r400 = retrieval["per_review"]["R100"], retrieval["per_review"]["R400"]
    assert r100["pdf_http_requests"] == r100["pdf_http_responses"] == 1
    assert r100["pdf_http_status"] == 200 and r100["pdf_curl_exitcode"] == 0
    assert r100["pdf_content_length"] == r100["pdf_size_download"] == 2117533
    assert r400["PDF_transport_attempts_including_zero_byte_DNS_failure"] == 3
    assert r400["PDF_body_HTTP_responses"] == 2
    proof = r400["completion_receipt"]
    assert proof["initial_body_bytes"] == 2796338
    assert proof["continuation_body_bytes"] == 5942210
    assert proof["initial_body_bytes"] + proof["continuation_body_bytes"] == proof["bytes"] == 8738548
    assert proof["distinct_manuscripts"] == 1 and proof["pdf_body_responses"] == 2
    assert proof["sha256"] == PDF_HASHES["R400"]
    assert proof["etag"] == '"8556f4-6357c4bd91a40"'
    assert packet()["adjudication"]["scientific_source_retrievals_during_adjudication"] == 0


def test_only_two_existing_public_papers_and_three_map_records_have_type_metadata_changes():
    old, live = published_context(BASE), published_context(PUBLISHED)
    assert old["papers"].keys() == live["papers"].keys()
    assert {pid for pid in old["papers"] if old["papers"][pid] != live["papers"][pid]} == set(TARGETS.values())
    assert sum(old["papers"][pid] == live["papers"][pid] for pid in old["papers"] if pid not in TARGETS.values()) == 672
    for rid, paper_id in TARGETS.items():
        expected = deepcopy(old["papers"][paper_id])
        expected["research_types"] = FINAL_TYPES[rid]
        expected["taxonomy_review"]["research_types"]["reason"] = CSV_UPDATES[TAXONOMY][rid]["research_types_review_reason"]
        assert live["papers"][paper_id] == expected
    assert old["pairs"] == live["pairs"]
    for path in PUBLIC:
        before, after = json.loads(published_bytes(BASE, path)), json.loads(published_bytes(PUBLISHED, path))
        oldmeta, newmeta = deepcopy(before["metadata"]), deepcopy(after["metadata"])
        oldmeta.pop("public_preview_generated_at", None)
        newmeta.pop("public_preview_generated_at", None)
        assert oldmeta == newmeta
        assert {k: v for k, v in before.items() if k not in {"metadata", "records"}} == {
            k: v for k, v in after.items() if k not in {"metadata", "records"}}
    before = {r["id"]: r for r in json.loads(published_bytes(BASE, PUBLIC[1]))["records"]}
    after = {r["id"]: r for r in json.loads(published_bytes(PUBLISHED, PUBLIC[1]))["records"]}
    assert before.keys() == after.keys() and len(before) == 1410
    expected_maps = {rid: {key for key, row in before.items() if row.get("paper_id") == pid} for rid, pid in TARGETS.items()}
    assert {rid: len(ids) for rid, ids in expected_maps.items()} == {"R100": 2, "R400": 1}
    target_ids = set.union(*expected_maps.values())
    assert {key for key in before if before[key] != after[key]} == target_ids
    assert sum(before[key] == after[key] for key in before if key not in target_ids) == 1407
    target_to_review = {pid: rid for rid, pid in TARGETS.items()}
    for key, row in before.items():
        expected = deepcopy(row)
        rid = target_to_review.get(row.get("paper_id"))
        if rid:
            expected["research_types"] = FINAL_TYPES[rid]
            expected["taxonomy_review"]["research_types"]["reason"] = CSV_UPDATES[TAXONOMY][rid]["research_types_review_reason"]
        assert after[key] == expected, key


def test_live_corpus_and_taxonomy_recompute_only_dataset_and_benchmark_additions():
    old, live = published_context(BASE), published_context(PUBLISHED)
    assert live["counts"] == old["counts"] == packet()["corpus_counts"] == CURRENT_CORPUS_COUNTS
    def totals(context):
        return Counter(label for row in context["papers"].values() for dimension in ("tasks", "research_types") for label in row[dimension])
    before, after = totals(old), totals(live)
    assert after == packet()["taxonomy_counts"]
    assert after == {"detection": 621, "source_attribution": 84, "localization": 45,
                     "method": 578, "dataset": 135, "benchmark": 92, "survey": 21, "analysis_study": 82}
    assert load_context()["counts"] == CURRENT_CORPUS_COUNTS
    assert totals(load_context()) == CURRENT_TAXONOMY_TOTALS
    assert not before - after and after - before == {"dataset": 1, "benchmark": 1}
    assert before["dataset"] == 134 and after["dataset"] == 135
    assert before["benchmark"] == 91 and after["benchmark"] == 92
    for rid, pid in TARGETS.items():
        assert old["papers"][pid]["tasks"] == live["papers"][pid]["tasks"] == ["detection"]
        assert old["papers"][pid]["image_scopes"] == live["papers"][pid]["image_scopes"] == ["fully_generated"]


def test_original_questions_locked_R1_R2_T2_and_unrelated_authoritative_tables_are_unchanged():
    queues = load_queues()
    taxonomy = {r["review_id"]: r for r in queues["taxonomy_review"]["records"]}
    for rid in TARGETS:
        assert record(packet(), rid)["original_review"] == taxonomy[rid]
    ledger = json.loads((ROOT / (AUDIT + "batch_c_policy_decisions.json")).read_bytes())
    by_id = {p["policy_id"]: p for p in ledger["policies"]}
    assert packet()["locked_policy_ledger"]["policies"] == [by_id[k] for k in ("T2", "R1", "R2")]
    assert "systematic comparative framework" in by_id["R2"]["final_rule"]
    assert "construction, release, curation" in by_id["R1"]["final_rule"]
    assert "Artifact segmentation qualifies" in by_id["T2"]["final_rule"]
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
    for name in ("taxonomy_review", "publication_metadata_review", "relationship_review", "unmapped_papers", "batch_c_policy_decisions"):
        path = AUDIT + name + ".json"
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_original_and_current_source_hashes_are_portable_and_ignore_no_scientific_change():
    old, new = original(), packet()
    assert new["source_files_sha256"] == old["source_files_sha256"]
    current = new["current_source_sha256"]
    assert current.keys() == old["source_files_sha256"].keys()
    assert len(current) == 13
    assert {p for p in current if current[p] != old["source_files_sha256"][p]} == {PAPERS, TAXONOMY, DECISIONS, *PUBLIC}
    tracked = set(baseline_paths())
    entries = {r["path"]: r for r in json.loads(published_bytes(BASE, FIXTURES))["entries"]}
    for path, expected in current.items():
        if path in tracked:
            raw = published_bytes(PUBLISHED, path)
        else:
            # Verify immutable committed fixture bytes, never a developer's runtime cache.
            entry = entries[path]
            assert entry["compression"] == "none"
            raw = published_bytes(BASE, entry["source"])
            assert digest(raw) == entry["sha256"] == entry["source_sha256"]
            assert len(raw) == entry["bytes"]
        assert digest(raw) == expected, path


def test_eighteen_prior_B_receipts_and_all_historical_fixture_bytes_remain_frozen():
    prior = original()["prior_B1A_I_artifact_sha256"]
    assert len(prior) == 18
    for path, expected in prior.items():
        assert digest(published_bytes(BASE, path)) == expected
        assert digest((ROOT / path).read_bytes()) == expected, path
    for path in baseline_paths("tests/fixtures"):
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_49_NeurIPS_artifacts_C13_and_separate_39_inventory_are_preserved():
    path = "data/raw/systematic_gap_migration_2026_10_03/baseline.json"
    raw = (ROOT / path).read_bytes()
    assert raw == published_bytes(BASE, path)
    frozen = json.loads(raw)["frozen_sha256"]
    assert len(frozen) == 49
    for relative, expected in frozen.items():
        assert digest(preserved_bytes(ROOT, relative)) == expected, relative
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
    for paper_id in intake["candidate_to_paper"].values():
        assert live["papers"][paper_id] == published_context(BASE)["papers"][paper_id]
        assert live["papers"][paper_id]["has_map_location"] is False
    for path in ("data/raw/corpus_quality_batch_c_closeout_2026_10_11/evidence_manifest.json",
                 "docs/corpus_quality_batch_c_closeout_2026_10_11.md",
                 "docs/corpus_quality_batch_c_evidence_debt_triage_2026_10_08.md",
                 "tests/test_corpus_quality_batch_c_closeout.py"):
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path), path


def test_report_and_packet_record_exact_scope_and_preserve_the_entire_original_report():
    data, report = packet(), (ROOT / REPORT).read_text()
    for token in (*IDS.values(), "R100", "R400", "PROPOSE_CORRECTION_ACCEPTED", "dataset", "benchmark",
                  "141", "143", "130", BASE, "OUT_OF_SCOPE_TASK_TAXONOMY_OBSERVATION",
                  "7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA"):
        assert token in report
    for token in ("empty", "unverified", "28", "27", "aggregation", "medium"):
        assert token in report.casefold()
    assert archived_bytes("report").decode() in report
    assert data["scope"]["review_decisions_added"] == data["scope"]["review_actions_closed"] == 2
    assert data["scope"]["authoritative_scientific_changes"] == 2
    assert data["scope"]["forensic_task_changes"] == 0
    assert data["scope"]["new_Batch_B_actions_added"] == 0
    assert data["scope"]["Batch_B_denominator_changes"] == 0
    # Final validation/export/publication fields are completion receipts, not science.


@pytest.mark.parametrize("rid", ["R100", "R400"])
def test_live_B1J_accepted_rows_public_records_map_records_and_terminal_prefix_remain_exact(rid):
    """Later audits may change other papers without rewriting B1J's accepted result."""
    pid = TARGETS[rid]
    for path in (PAPERS, TAXONOMY):
        assert selected_row((ROOT / path).read_bytes(), pid) == selected_row(published_bytes(PUBLISHED, path), pid)
    historical, live = published_context(PUBLISHED), load_context()
    assert live["papers"][pid] == historical["papers"][pid]
    assert {pair: n for pair, n in live["pairs"].items() if pair[0] == pid} == {
        pair: n for pair, n in historical["pairs"].items() if pair[0] == pid}
    before = {r["id"]: r for r in json.loads(published_bytes(PUBLISHED, PUBLIC[1]))["records"] if r.get("paper_id") == pid}
    after = {r["id"]: r for r in json.loads((ROOT / PUBLIC[1]).read_bytes())["records"] if r.get("paper_id") == pid}
    assert before == after and len(after) == {"R100": 2, "R400": 1}[rid]
    raw = (ROOT / DECISIONS).read_bytes()
    prefix = published_bytes(PUBLISHED, DECISIONS)
    assert raw.startswith(prefix) and len(csv_records(prefix)) == 91
    rows = read_review_decisions(ROOT / DECISIONS)
    assert rows[:91] == csv_records(prefix)
    assert terminal(rows)[rid] == IDS[rid]
    assert sum(r["decision_id"] == IDS[rid] for r in rows) == 1
