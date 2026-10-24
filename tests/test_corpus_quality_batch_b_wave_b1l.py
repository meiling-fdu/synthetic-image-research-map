"""B1L accepts two dataset resources while preserving their independent roles."""
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
BASE = "78f6ebae879f630eb6e386d92ab90252af09670d"
# B1L is a published transaction; its accepted rows and decisions also remain live guards.
PUBLISHED = "53c2a9aa0fa3a36427ea8e71966e29cdfba70153"
PAPERS = "data/curated/papers.csv"
TAXONOMY = "data/curated/paper_taxonomy.csv"
DECISIONS = "data/curated/review_decisions.csv"
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1l_2026_10_22/evidence_manifest.json"
REPORT = "docs/corpus_quality_batch_b_wave_b1l_2026_10_22.md"
AUDIT = "data/raw/corpus_quality_audit_2026_10_04/"
FIXTURES = "tests/fixtures/historical_test_fixture_manifest.json"
TARGETS = {"R181":"curated:bb388762c1cb4bd3bf4a", "R335":"curated:5ad6cb3411820ff01a03"}
FINAL_TYPES = {"R181":["method","dataset"], "R335":["dataset","benchmark"]}
IDS = {'R181': 'review:dff9bf2a84a9e1c0607f', 'R335': 'review:3d7ddf44e6b74745d848'}
CSV_UPDATES = {'data/curated/papers.csv': {'R181': {'research_types': 'method;dataset'},
                             'R335': {'research_types': 'dataset;benchmark'}},
 'data/curated/paper_taxonomy.csv': {'R181': {'research_types': 'method;dataset',
                                              'research_types_review_reason': 'R181 accepted under '
                                                                              'locked R1: complete '
                                                                              'arXiv 2604.15027v1 '
                                                                              'establishes '
                                                                              'AncesTree and '
                                                                              'ReWIND as '
                                                                              'substantive '
                                                                              'reusable '
                                                                              'image-quality and '
                                                                              'propagation '
                                                                              'resources '
                                                                              'independently of '
                                                                              'QuAD, with '
                                                                              'structured '
                                                                              'degradation '
                                                                              'construction, web '
                                                                              'near-duplicate '
                                                                              'curation and '
                                                                              'evaluation using '
                                                                              'six detection '
                                                                              'methods. Add '
                                                                              'dataset; retain '
                                                                              'method, detection '
                                                                              'and '
                                                                              'fully_generated. '
                                                                              'AncesTree has 1,100 '
                                                                              'roots and 136,400 '
                                                                              'descendants; ReWIND '
                                                                              'has 9,646 instances '
                                                                              'and 162 groups. '
                                                                              'Mean balanced '
                                                                              'accuracy 73.2 to '
                                                                              '81.6 and 63.0 to '
                                                                              '70.3 is not '
                                                                              'universal '
                                                                              'improvement. '
                                                                              'Complete release, '
                                                                              'licensing, exact '
                                                                              'source-group '
                                                                              'partitions, '
                                                                              'leave-one-out unit, '
                                                                              'leakage safeguards, '
                                                                              'publisher-final '
                                                                              'equivalence and '
                                                                              'numerical '
                                                                              'reproduction remain '
                                                                              'unverified; results '
                                                                              'apply to reviewed '
                                                                              'arXiv v1. Actual '
                                                                              'download '
                                                                              'availability is not '
                                                                              'the sole R1 '
                                                                              'criterion.',
                                              'research_types_evidence_tier': 'primary_paper',
                                              'research_types_evidence_source': 'https://arxiv.org/pdf/2604.15027v1',
                                              'research_types_evidence_excerpt': 'ArXiv '
                                                                                 '2604.15027v1: '
                                                                                 'AncesTree 100 '
                                                                                 'real plus 1,000 '
                                                                                 'synthetic roots; '
                                                                                 'five degradation '
                                                                                 'levels, 124 '
                                                                                 'descendants per '
                                                                                 'root, 136,400 '
                                                                                 'descendants '
                                                                                 'excluding roots, '
                                                                                 'crop-resize-compression '
                                                                                 'construction. '
                                                                                 'ReWIND 9,646 '
                                                                                 'instances (4,367 '
                                                                                 'real and 5,279 '
                                                                                 'fake), 162 '
                                                                                 'groups. '
                                                                                 'Six-detector '
                                                                                 'mean bAcc/NLL: '
                                                                                 'AncesTree naive '
                                                                                 '73.2/.75 to QuAD '
                                                                                 '81.6/.43; ReWIND '
                                                                                 '63.0/1.27 to '
                                                                                 '70.3/.63. These '
                                                                                 'are means; '
                                                                                 'CO-SPY ReWIND '
                                                                                 '62.3/.83 is '
                                                                                 'worse than naive '
                                                                                 '65.7/.81. '
                                                                                 'Source-group '
                                                                                 'split, '
                                                                                 'leave-one-out '
                                                                                 'unit, licensing, '
                                                                                 'full release and '
                                                                                 'publisher-final '
                                                                                 'equivalence '
                                                                                 'remain '
                                                                                 'unverified.',
                                              'audited_at': '2026-10-23'},
                                     'R335': {'research_types': 'dataset;benchmark',
                                              'research_types_review_reason': 'R335 accepted under '
                                                                              'locked R1: complete '
                                                                              'arXiv 2606.18554v1 '
                                                                              'establishes a '
                                                                              'substantive curated '
                                                                              'and generated '
                                                                              'disaster-image '
                                                                              'resource '
                                                                              'independently of '
                                                                              'the retained '
                                                                              'benchmark '
                                                                              'evaluation '
                                                                              'contribution. Add '
                                                                              'dataset; retain '
                                                                              'benchmark, '
                                                                              'detection and '
                                                                              'fully_generated; no '
                                                                              'method. The corpus '
                                                                              'has 6,000 real and '
                                                                              '24,000 synthetic '
                                                                              'images across four '
                                                                              'categories and four '
                                                                              'generators; '
                                                                              'original '
                                                                              'construction '
                                                                              'includes real-image '
                                                                              'curation, Moondream '
                                                                              'captions, Llama 3 '
                                                                              'refinement and '
                                                                              'diffusion '
                                                                              'generation. '
                                                                              'Fine-tuned 18 '
                                                                              'unseen subsets and '
                                                                              'zero-shot 20 '
                                                                              'subsets are '
                                                                              'distinct. Public '
                                                                              'assets, rights, '
                                                                              'license, exact '
                                                                              'splits, leakage '
                                                                              'safeguards, '
                                                                              'publisher-final '
                                                                              'equivalence and '
                                                                              'reproduction remain '
                                                                              'unverified; numeric '
                                                                              'inconsistencies and '
                                                                              '12 repeated CGL '
                                                                              'values are '
                                                                              'preserved. '
                                                                              'Canonical year 2025 '
                                                                              'and all publication '
                                                                              'metadata remain '
                                                                              'unchanged despite '
                                                                              '2026 preprint and '
                                                                              'first-online and '
                                                                              '2027 citation '
                                                                              'chronology.',
                                              'research_types_evidence_tier': 'primary_paper',
                                              'research_types_evidence_source': 'https://arxiv.org/pdf/2606.18554v1',
                                              'research_types_evidence_excerpt': 'ArXiv '
                                                                                 '2606.18554v1: '
                                                                                 '30,000 images = '
                                                                                 '6,000 real plus '
                                                                                 '24,000 '
                                                                                 'synthetic; Fire, '
                                                                                 'Earthquake, '
                                                                                 'Flood and '
                                                                                 'Thunderstorm; '
                                                                                 'SD1.5, SD2.0, '
                                                                                 'SDXL and PixArt. '
                                                                                 'Moondream '
                                                                                 'captions, Llama '
                                                                                 '3 prompts and '
                                                                                 'text-to-image '
                                                                                 'generation. '
                                                                                 'Fine-tune 1,500 '
                                                                                 'real plus 1,500 '
                                                                                 'SD1.5 earthquake '
                                                                                 'images; 18 '
                                                                                 'unseen subsets '
                                                                                 'versus 20 '
                                                                                 'zero-shot '
                                                                                 'subsets. CGL '
                                                                                 'fake-Flood '
                                                                                 '99.68% (SD1.5) '
                                                                                 'versus 1.46% '
                                                                                 '(SD2.0) is '
                                                                                 'per-subset '
                                                                                 'accuracy, not '
                                                                                 'pooled '
                                                                                 'performance. '
                                                                                 'Twelve repeated '
                                                                                 'CGL values and '
                                                                                 'backbone and '
                                                                                 'prose-table '
                                                                                 'contradictions '
                                                                                 'remain; complete '
                                                                                 'assets, rights, '
                                                                                 'license, splits, '
                                                                                 'leakage '
                                                                                 'safeguards and '
                                                                                 'final-version '
                                                                                 'equivalence '
                                                                                 'unverified. '
                                                                                 'Existing '
                                                                                 'benchmark '
                                                                                 'retained.',
                                              'audited_at': '2026-10-23'}}}
CSV_AFTER_HASHES = {'data/curated/papers.csv': '19158ec10a6137cafea4b879ee89254363b89246196dae84db857ed19238f788',
 'data/curated/paper_taxonomy.csv': 'c2bcf030e710804140bac7c8826429c6612194509d1b9d64c1382fe1f4cbd2e4'}
EVIDENCE_HASHES = {
    "manifest":"eaf4b9f4dcbdd63ec42da38a3c74404c71aa9ceb488e17b23c83e03b55bb60f3",
    "report":"7d8ad6de38d87b8d45c5bd1a7d8b320133c3e26ce88746ba0799900a2f121755",
}
PDF_HASHES = {"R181":"50f03fe6fc43c628b763a56d76582706a210e15806a1ac94e2c925ca6cef5415",
              "R335":"ac3a0f8e7a8b0751991420898bb31e4b3dadf8f629360cddde4547b2d4d27dc1"}
WORKER_HASHES = {"R181":"cc301fe6bc87944a98e9dccffb6f494be7106ef4bd621f75b221aea568af6352",
                 "R335":"549054cd1af77d175fdc4db8cf78ab3d561ddf191afb2a30cbf9b161b5db3450"}


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


@pytest.mark.parametrize("kind",["manifest","report"])
def test_original_evidence_packet_is_losslessly_archived_with_exact_hashes(kind):
    assert archived_bytes(kind)
    assert set(packet()["evidence_only_packet_archives"]) == {"manifest","report"}
    assert original()["baseline_commit"] == packet()["baseline_commit"] == BASE
    assert original()["scope"]["authoritative_data_changes"] == 0
    assert original()["scope"]["review_decisions_added"] == 0


def test_original_worker_and_independent_receipts_keep_actual_counts_and_numeric_transcriptions():
    old = original()
    for rid,count in (("R181",51),("R335",28)):
        assert old["validation"]["worker_checks"][rid] == {"passed":count,"failed":0}
        receipt = old["worker_validation"][rid]["receipt"]
        assert receipt["passed"] == count and receipt["failed"] == 0
        assert all(c["passed"] for c in receipt["checks"])
    independent = old["independent_review_findings"]["independent-scientific-crossreview.json"]["receipt"]
    assert independent["passed"] == 61 and independent["failed"] == 0
    assert independent["numeric_values_compared"] == {"R181":406,"R335_reused":354}
    assert sum(independent["numeric_values_compared"].values()) == 760
    assert independent["numeric_mismatched_rows"] == independent["scientific_disagreements"] == []
    assert independent["worker_review_sha256"] == WORKER_HASHES
    assert old["validation"]["final_preservation_receipt"]["passed"] == 37
    # The original prepared-packet review is distinct from the later 15-check boundary receipt.
    assert old["validation"]["independent_packet_assembly_review"]["passed"] == 12
    annotation = old["non_scientific_checker_label_annotation"]["receipt"]
    assert annotation["actual_asserted_primary_value"] == 99.43
    assert annotation["receipts_changed"] is False and annotation["scientific_changes"] == 0


@pytest.mark.parametrize("path",[PAPERS,TAXONOMY])
def test_exact_four_rows_fourteen_existing_cells_change_and_all_other_csv_bytes_survive(path):
    before_raw,after_raw = published_bytes(BASE,path),published_bytes(PUBLISHED,path)
    before,after = csv_records(before_raw),csv_records(after_raw)
    identity = "taxonomy_id" if path == TAXONOMY else "paper_id"
    assert [r[identity] for r in before] == [r[identity] for r in after]
    assert len({r[identity] for r in after}) == len(after)
    assert {r["paper_id"] for r,s in zip(before,after) if r != s} == set(TARGETS.values())
    for rid,pid in TARGETS.items():
        old,new = selected_row(before_raw,pid),selected_row(after_raw,pid)
        edits = CSV_UPDATES[path][rid]
        assert new == {**old,**edits}
        assert {k for k in old if old[k] != new[k]} == edits.keys()
        assert new["research_types"] == ";".join(FINAL_TYPES[rid])
        assert new["tasks"] == old["tasks"] == "detection"
        assert new["image_scopes"] == old["image_scopes"] == "fully_generated"
        if path == PAPERS:
            assert set(edits) == {"research_types"}
        else:
            assert set(edits) == {"research_types","research_types_review_reason","research_types_evidence_tier",
                                  "research_types_evidence_source","research_types_evidence_excerpt","audited_at"}
            assert new["research_types_evidence_tier"] == "primary_paper"
            assert new["audited_at"] == "2026-10-23"
            assert new["research_types_status"] == old["research_types_status"] == "reviewed"
            assert new["research_types_evidence_source"] == record(original(),rid)["source"]["url"]
    header = next(csv.reader(io.StringIO(before_raw.decode(),newline="")))
    chunks = logical_csv_chunks(before_raw)
    by_id = {pid:rid for rid,pid in TARGETS.items()}
    expected = [chunks[0]]
    for row,chunk in zip(before,chunks[1:]):
        rid = by_id.get(row["paper_id"])
        expected.append(replace_csv_tokens(chunk,header,CSV_UPDATES[path][rid]) if rid else chunk)
    assert after_raw == b"".join(expected)
    assert digest(after_raw) == CSV_AFTER_HASHES[path]


def test_two_terminal_appends_preserve_all_92_prior_decisions_and_bytes():
    before,after = published_bytes(BASE,DECISIONS),published_bytes(PUBLISHED,DECISIONS)
    old,rows = csv_records(before),csv_records(after)
    assert after.startswith(before) and rows[:-2] == old
    assert len(old) == 92 and len(rows) == 94
    assert len({r["decision_id"] for r in rows}) == len(rows)
    assert terminal(rows) == {**terminal(old),**IDS}
    assert [r["decision_id"] for r in rows[-2:]] == list(IDS.values())
    for rid,row in zip(TARGETS,rows[-2:]):
        assert row["decision_id"] == IDS[rid]
        assert row["review_queue"] == "other" and row["review_queue"] in ALLOWED_REVIEW_QUEUES
        assert row["target_type"] == "paper" and row["institution"] == ""
        assert row["action"] == "no_action_after_review" and row["action"] in ALLOWED_REVIEW_ACTIONS
        assert row["created_by"] == "maintainer-approved-batch-b-b1l"
        assert row["created_at"] == row["updated_at"]
        assert row["created_at"] >= record(original(),rid).get("recorded_at_utc","2026-10-22T00:00:00+00:00")
        assert datetime.fromisoformat(row["created_at"].replace("Z","+00:00")).tzinfo == timezone.utc
        prior = selected_row(published_bytes(BASE,PAPERS),TARGETS[rid])
        for field in ("title","year","doi","openalex_url"):
            assert row[field] == prior[field]
        identity = "|".join(" ".join(row[k].split()).casefold() for k in
                            ("review_queue","target_type","doi","openalex_url","title","year","institution"))
        assert "review:" + digest(identity.encode())[:20] == IDS[rid]
        assert row["review_note"].startswith("Batch B review "+rid+";")
        assert "PROPOSE_CORRECTION_ACCEPTED" in row["review_note"]
        assert "R1" in row["review_note"] and PDF_HASHES[rid] in row["review_note"]
        assert packet()["adjudication"]["terminal_decisions"][rid] == row
    adjudication = packet()["adjudication"]
    assert adjudication["decision_ids"] == IDS
    assert adjudication["registry_rows_before"] == 92 and adjudication["registry_rows_after"] == 94
    assert adjudication["prior_decision_bytes_preserved"] is True
    assert adjudication["before_registry_sha256"] == digest(before)
    assert adjudication["after_registry_sha256"] == digest(after)
    assert adjudication["existing_csv_cells_changed"] == 14
    changes = adjudication["csv_changes"]
    assert len(changes) == 4
    assert {(x["path"],x["row_identity"]["paper_id"]) for x in changes} == {
        (path,pid) for path in (PAPERS,TAXONOMY) for pid in TARGETS.values()}
    by_id = {pid:rid for rid,pid in TARGETS.items()}
    for change in changes:
        path,rid = change["path"],by_id[change["row_identity"]["paper_id"]]
        assert change["after_fields"] == CSV_UPDATES[path][rid]
        assert change["planned_after_sha256"] == CSV_AFTER_HASHES[path]


@pytest.mark.parametrize("rid",["R181","R335"])
def test_terminal_upsert_is_idempotent_without_byte_or_timestamp_churn(tmp_path,rid):
    path = tmp_path/"review_decisions.csv"
    raw = (ROOT/DECISIONS).read_bytes()
    path.write_bytes(raw)
    row = next(r for r in read_review_decisions(path) if r["decision_id"] == IDS[rid])
    assert upsert_review_decision(row,path=path) == row
    assert path.read_bytes() == raw


def test_only_R181_R335_close_and_distinct_affected_papers_are_recomputed():
    before = accounting(csv_records(published_bytes(BASE,DECISIONS)),published_context(BASE)["papers"])
    after = accounting(csv_records(published_bytes(PUBLISHED,DECISIONS)),published_context(PUBLISHED)["papers"])
    assert after == packet()["batch_b_accounting"]
    fields = ("historical_actions","historical_papers","historical_unresolved_actions",
              "active_public_unresolved_actions","active_public_unresolved_papers")
    assert [before[k] for k in fields] == [159,148,142,140,129]
    assert [after[k] for k in fields] == [159,148,140,138,127]
    assert before["historical_unresolved_papers"] == 131 and after["historical_unresolved_papers"] == 129
    assert set(after["closed_review_ids"]) - set(before["closed_review_ids"]) == set(TARGETS)
    for field in ("historical_unresolved_review_ids","active_public_unresolved_review_ids"):
        assert after[field] == [rid for rid in before[field] if rid not in TARGETS]
    ledger = [r for r in decision_rows(load_queues()) if r["batch"] == "B"]
    for rid,pid in TARGETS.items():
        assert [(r["review_id"],r.get("dimension")) for r in ledger if r["paper_id"] == pid] == [(rid,"research_types")]
    assert {"R467","P467","R267","T046","T093","T608","T526","P526"} <= set(after["active_public_unresolved_review_ids"])


def test_complete_original_scientific_records_and_source_receipts_survive_acceptance_losslessly():
    old,new = original(),packet()
    assert [r["review_id"] for r in new["records"]] == ["R181","R335"]
    flags = {"maintainer_acceptance_pending","review_closed","authoritative_changes_applied","terminal_review_decision_created"}
    for rid in TARGETS:
        prior,accepted = record(old,rid),record(new,rid)
        for key in prior:
            if key not in flags:
                assert accepted[key] == prior[key],(rid,key)
        assert accepted["maintainer_acceptance_pending"] is False
        assert all(accepted[k] is True for k in flags-{"maintainer_acceptance_pending"})
        assert accepted["terminal_review_decision_id"] == IDS[rid]
        assert accepted["accepted_outcome"] == "PROPOSE_CORRECTION_ACCEPTED"
        assert accepted["final_authoritative_taxonomy"] == {"tasks":["detection"],"image_scopes":["fully_generated"],"research_types":FINAL_TYPES[rid]}
    mutable = {"phase","scope","validation","integrity","corpus_counts","taxonomy_counts","batch_b_accounting","git_requirements"}
    for key in old:
        if key not in mutable|{"records"}:
            assert new[key] == old[key],key
    for key in mutable:
        assert new["evidence_only_"+key] == old[key],key


@pytest.mark.parametrize("rid,pages,bytes",[("R181",10,1215364),("R335",15,6249493)])
def test_exact_reviewed_arxiv_versions_are_preserved_without_publisher_final_equivalence(rid,pages,bytes):
    source = record(packet(),rid)["source"]
    assert source["sha256"] == PDF_HASHES[rid] and source["pages"] == pages and source["bytes"] == bytes
    assert source["pages_read"] == list(range(1,pages+1)) and source["full_manuscript_read"] is True
    if rid == "R181":
        assert source["url"] == "https://arxiv.org/pdf/2604.15027v1"
        assert source["publication_final_equivalence_verified"] is False
        assert "No direct comparison" in source["version"]
    else:
        assert source["url"] == "https://arxiv.org/pdf/2606.18554v1"
        assert "not certified" in source["version"]
        assert "Unavailable/unverified" in source["original_transport_receipt"]


def test_R181_systematic_resource_counts_and_generation_order_are_preserved():
    r = record(packet(),"R181")
    assert r["provisional_outcome"] == "DATASET_ADDITION_SUPPORTED"
    assert r["proposed_complete_research_types"] == ["method","dataset"]
    a,w = r["AncesTree"],r["ReWIND"]
    assert a["source_real_images"] == 100 and a["source_fake_images"] == 1000
    assert a["source_groups"] == 1100 and a["variants_per_root_excluding_root"] == 124
    assert a["images_total"] == a["source_groups"]*a["variants_per_root_excluding_root"] == 136400
    assert a["depth"] == 5 and a["nodes_by_level"] == [4,8,16,32,64]
    assert sum(a["nodes_by_level"]) == 124 and a["root_included"] is False
    assert a["operations"]["order"] == ["cropping","resizing","compression"]
    assert [a["operations"][k] for k in ("crop_probability","resize_probability","compression_probability")] == [0.5,0.6,0.95]
    assert a["operations"]["retained_area_percent"] == [60,99.9]
    assert a["operations"]["shorter_side_pixels"] == [256,2048]
    assert w["source_groups"] == w["real_sources"]+w["fake_sources"] == 162
    assert w["instances_total"] == w["real_instances"]+w["fake_instances"] == 9646
    assert (w["real_instances"],w["fake_instances"]) == (4367,5279)
    assert len(r["question_matrix"]) == 15 and len(a["generator_families"]) == 10


def test_R181_experimental_means_counterexamples_and_split_uncertainty_are_preserved():
    r = record(packet(),"R181")
    q,p = r["quantitative_evidence"],r["protocol"]
    assert p["base_detector_order"] == ["DMID","CoDE","D3","B-Free","DRCT","CO-SPY"]
    assert q["principal_comparisons"]["AncesTree_naive_bAcc_NLL"] == [73.2,0.75]
    assert q["principal_comparisons"]["AncesTree_QuAD_bAcc_NLL"] == [81.6,0.43]
    assert q["principal_comparisons"]["ReWIND_naive_bAcc_NLL"] == [63.0,1.27]
    assert q["principal_comparisons"]["ReWIND_transferred_QuAD_bAcc_NLL"] == [70.3,0.63]
    assert q["principal_comparisons"]["ReWIND_leave_one_out_QuAD_star_bAcc_NLL"] == [71.4,0.57]
    assert p["split_scope_verified"] is False and "source-group" in p["split_limitations"]
    assert "unspecified" in p["ReWIND_QuAD_star"]
    assert len(q["nonuniform_results"]) == 4
    assert any("CO-SPY" in x for x in q["nonuniform_results"]) and any("B-Free" in x for x in q["nonuniform_results"])
    assert len(q["Table2"]["rows"]) == 13 and len(q["Table3"]["rows"]) == 16
    assert sum(len(row["values"])*2 for name in ("Table2","Table3") for row in q[name]["rows"]) == 406
    assert "causal dataset-diversity-only" in q["causal_boundary"]


def test_R181_release_listings_are_not_misrepresented_as_complete_images_splits_or_license():
    release = record(packet(),"R181")["release_review"]
    assert release["metadata_requests_by_root"] == 10 and release["metadata_HTTP_200"] == 7
    assert release["metadata_zero_byte_timeouts"] == 3
    assert release["CSV_bodies_downloaded"] == 0 and release["image_payloads_downloaded"] == 0
    assert release["complete_public_release_verified"] is False
    assert release["immutable_official_splits_verified"] is False
    assert release["parent_child_metadata_contents_verified"] is False
    assert release["dataset_license_verified"] is False and release["article_or_code_license_not_assumed_for_images"] is True
    assert release["GitHub_license_classification"]["spdx_id"] == "NOASSERTION"
    assert len(release["failed_text_requests"]) == 3
    assert all(x["curl_exit_code"] == 28 and x["body_bytes"] == 0 and x["retry"] is False for x in release["failed_text_requests"])


def test_R335_original_corpus_role_and_stratified_counts_coexist_with_benchmark():
    r = record(packet(),"R335")
    assert r["provisional_outcome"] == "DATASET_ADDITION_SUPPORTED"
    assert r["proposed_complete_research_types"] == ["dataset","benchmark"] and "method" not in r["proposed_complete_research_types"]
    counts = r["dataset_counts"]
    assert counts["published_total"] == counts["published_real"]+counts["published_synthetic"] == 30000
    assert counts["published_real"] == 6000 and counts["published_synthetic"] == 24000
    assert counts["categories"] == ["Fire","Earthquake","Flood","Thunderstorm"]
    assert counts["generators"] == ["SD 1.5","SD 2.0","SDXL","PixArt"]
    assert counts["real_to_synthetic_ratio"] == "1:4"
    assert all(row["real"] == 1500 and all(row[g] == 1500 for g in counts["generators"]) for row in counts["table_1_rows"])
    assert counts["downloaded_asset_inventory_counted"] is False
    assert r["original_contribution_analysis"]["separate_benchmark_role"]
    questions = " ".join(x["finding"] for x in r["question_matrix"])
    assert "Moondream" in questions and "Llama" in questions


def test_R335_18_unseen_and20_zero_shot_subsets_are_not_pooled_accuracy():
    r = record(packet(),"R335")
    protocol = r["experimental_protocol"]
    assert protocol["OOD_test_subsets"] == 18 and protocol["zero_shot_test_subsets"] == 20
    assert "1,500 images per class" in protocol["fine_tune_train_domain"] and "SD 1.5" in protocol["fine_tune_train_domain"]
    assert protocol["exact_split_files_verified"] is False and protocol["all_remaining_27000_images_tested_verified"] is False
    assert "not an aggregate binary accuracy" in protocol["metric_boundary"]
    tables = {x["table"]:x for x in r["quantitative_tables"]}
    assert [len(tables[n]["rows"]) for n in (2,3,4)] == [18,18,20]
    assert [len(tables[n]["columns"]) for n in (2,3,4)] == [6,7,6]
    assert sum(len(row["accuracy_percent"]) for tab in tables.values() for row in tab["rows"]) == 354
    by_subset = {row["subset"]:row["accuracy_percent"] for row in tables[3]["rows"]}
    assert by_subset["Flood - SD 1.5"]["CGL"] == "99.68"
    assert by_subset["Flood - SD 2.0"]["CGL"] == "1.46"
    assert all(tab["numbers_retained_as_printed"] is True and tab["independent_reproduction"] is False for tab in tables.values())


def test_R335_repeated_CGL_cells_and_numerical_contradictions_are_not_silently_fixed():
    r = record(packet(),"R335")
    tables = {x["table"]:x for x in r["quantitative_tables"]}
    rows3 = {x["subset"]:x["accuracy_percent"] for x in tables[3]["rows"]}
    rows4 = {x["subset"]:x["accuracy_percent"] for x in tables[4]["rows"]}
    repeated = r["cross_protocol_repeated_CGL_cells"]
    assert len(repeated) == 12
    for row in repeated:
        assert rows3[row["fine_tuned_subset"]]["CGL"] == rows4[row["zero_shot_subset"]]["CGL"] == row["accuracy_percent"]
    rows2 = {x["subset"]:x["accuracy_percent"] for x in tables[2]["rows"]}
    assert rows2["Thunderstorm - SD 1.5"]["ConvNeXt"] == "9.84"
    assert rows2["Thunderstorm - PixArt"]["ConvNeXt"] == "0.00"
    assert rows2["Flood - SD 1.5"]["ViT"] == "99.43"
    limitations = " ".join(r["limitations_and_competing_evidence"])
    for token in ("98.1%","49.7%","eight backbones","enumerates six","Twelve CGL","globally 6,000 real versus 24,000 synthetic"):
        assert token in limitations


def test_R335_multiyear_publication_identity_is_explicit_and_authoritative_metadata_unchanged():
    r = record(packet(),"R335")
    chronology = r["publication_identity_reconciliation"]
    assert chronology["canonical_year_preserved"] == 2025 and "SOICT 2025" in chronology["conference_edition"]
    assert chronology["arxiv_submission"] == "2026-06-17T00:08:35Z"
    assert chronology["publisher_chapter_first_online"] == "2026-08-12"
    assert chronology["publisher_citation_copyright_year"] == 2027
    assert chronology["publisher_page_span"] == 16 and chronology["reviewed_author_manuscript_pages"] == 15
    assert chronology["publisher_final_manuscript_equivalence_verified"] is False
    assert chronology["publication_metadata_change_authorized"] is False
    assert chronology["new_publication_review_action_created"] is False
    before = selected_row(published_bytes(BASE,PAPERS),TARGETS["R335"])
    after = selected_row((ROOT/PAPERS).read_bytes(),TARGETS["R335"])
    for field in ("year","venue","venue_id","venue_name","venue_track","doi","arxiv_id","authors","paper_url"):
        assert before[field] == after[field]
    assert before["year"] == "2025" and before["doi"] == "10.1007/978-981-92-2600-9_17"
    release = r["resource_release_assessment"]
    assert release["downloadable_complete_dataset_verified"] is False and release["corpus_license_verified"] is False
    assert release["metadata_annotations_or_split_files_verified"] is False


def test_original_one_new_and_one_reused_manuscript_budget_is_preserved_with_no_adjudication_retrieval():
    retrieval = packet()["retrieval_accounting"]
    assert retrieval == original()["retrieval_accounting"]
    assert retrieval["new_complete_manuscripts_by_review"] == {"R181":1,"R335":0}
    assert retrieval["reused_complete_distinct_manuscripts_by_review"] == {"R181":0,"R335":1}
    assert retrieval["new_complete_manuscripts_total"] == 1 and retrieval["complete_distinct_manuscripts_reviewed_total"] == 2
    assert retrieval["new_full_manuscript_transfers_after_resume"] == 0
    transfer = retrieval["R181_successful_transfer_receipt"]
    assert transfer["process_exitcode"] == transfer["retries"] == 0
    assert transfer["body_bytes"] == 1215364 and transfer["body_sha256"] == PDF_HASHES["R181"]
    assert packet()["adjudication"]["scientific_source_retrievals_during_adjudication"] == 0
    assert packet()["workflow_recovery"] == original()["workflow_recovery"]


def test_exact_two_public_papers_and_six_dependent_maps_change_only_types_and_reason():
    old,live = published_context(BASE),published_context(PUBLISHED)
    assert old["papers"].keys() == live["papers"].keys() and len(live["papers"]) == 674
    assert {pid for pid in old["papers"] if old["papers"][pid] != live["papers"][pid]} == set(TARGETS.values())
    assert sum(old["papers"][pid] == live["papers"][pid] for pid in old["papers"] if pid not in TARGETS.values()) == 672
    for rid,pid in TARGETS.items():
        expected = deepcopy(old["papers"][pid])
        expected["research_types"] = FINAL_TYPES[rid]
        expected["taxonomy_review"]["research_types"]["reason"] = CSV_UPDATES[TAXONOMY][rid]["research_types_review_reason"]
        assert live["papers"][pid] == expected
    assert old["pairs"] == live["pairs"] and sum(live["pairs"].values()) == len(live["pairs"]) == 1410
    for path in PUBLIC:
        before,after = json.loads(published_bytes(BASE,path)),json.loads(published_bytes(PUBLISHED,path))
        oldmeta,newmeta = deepcopy(before["metadata"]),deepcopy(after["metadata"])
        oldmeta.pop("public_preview_generated_at",None)
        newmeta.pop("public_preview_generated_at",None)
        assert oldmeta == newmeta
        assert {k:v for k,v in before.items() if k not in {"records","metadata"}} == {k:v for k,v in after.items() if k not in {"records","metadata"}}
    before = {r["id"]:r for r in json.loads(published_bytes(BASE,PUBLIC[1]))["records"]}
    after = {r["id"]:r for r in json.loads(published_bytes(PUBLISHED,PUBLIC[1]))["records"]}
    assert before.keys() == after.keys() and len(before) == 1410
    by_paper = {pid:rid for rid,pid in TARGETS.items()}
    dependent = {rid:{key for key,row in before.items() if row.get("paper_id") == pid} for rid,pid in TARGETS.items()}
    assert {rid:len(ids) for rid,ids in dependent.items()} == {"R181":1,"R335":5}
    target_ids = set.union(*dependent.values())
    assert {key for key in before if before[key] != after[key]} == target_ids
    assert sum(before[key] == after[key] for key in before if key not in target_ids) == 1404
    for key,row in before.items():
        expected = deepcopy(row)
        rid = by_paper.get(row.get("paper_id"))
        if rid:
            expected["research_types"] = FINAL_TYPES[rid]
            expected["taxonomy_review"]["research_types"]["reason"] = CSV_UPDATES[TAXONOMY][rid]["research_types_review_reason"]
        assert after[key] == expected,key


def test_recomputed_live_counts_add_two_datasets_and_no_other_label_or_corpus_delta():
    old,live = published_context(BASE),published_context(PUBLISHED)
    assert old["counts"] == live["counts"] == packet()["corpus_counts"] == CURRENT_CORPUS_COUNTS
    def totals(context):
        return Counter(label for r in context["papers"].values() for dimension in ("tasks","research_types") for label in r[dimension])
    before,after = totals(old),totals(live)
    assert after == packet()["taxonomy_counts"]
    assert load_context()["counts"] == CURRENT_CORPUS_COUNTS
    assert totals(load_context()) == CURRENT_TAXONOMY_TOTALS
    assert not before-after and after-before == {"dataset":2}
    assert before["dataset"] == 135 and after["dataset"] == 137
    assert after == {"detection":621,"source_attribution":84,"localization":45,"method":578,
                     "dataset":137,"benchmark":91,"survey":21,"analysis_study":82}


def test_original_questions_policy_and_all_unrelated_authoritative_files_are_unchanged():
    queues = load_queues()
    by_id = {r["review_id"]:r for r in queues["taxonomy_review"]["records"]}
    for rid in TARGETS:
        assert record(packet(),rid)["original_review"] == by_id[rid]
    policy = json.loads((ROOT/(AUDIT+"batch_c_policy_decisions.json")).read_bytes())
    r1 = next(r for r in policy["policies"] if r["policy_id"] == "R1")
    assert packet()["locked_policy_ledger"]["policies"] == [r1]
    assert "Data generated or collected solely" in r1["final_rule"]
    allowed = {PAPERS,TAXONOMY,DECISIONS,*PUBLIC}
    for path in baseline_paths("data/curated","data/manual","web/data"):
        if path not in allowed:
            assert (ROOT/path).read_bytes() == published_bytes(BASE,path),path
    for name in ("taxonomy_review","publication_metadata_review","relationship_review","unmapped_papers","batch_c_policy_decisions"):
        path = AUDIT+name+".json"
        assert (ROOT/path).read_bytes() == published_bytes(BASE,path),path


def test_source_hashes_are_portable_and_change_only_five_authorized_dependencies():
    old,new = original(),packet()
    assert new["source_files_sha256"] == old["source_files_sha256"]
    current = new["current_source_sha256"]
    assert current.keys() == old["source_files_sha256"].keys()
    assert {path for path in current if current[path] != old["source_files_sha256"][path]} == {PAPERS,TAXONOMY,DECISIONS,*PUBLIC}
    tracked = set(baseline_paths())
    entries = {r["path"]:r for r in json.loads(published_bytes(BASE,FIXTURES))["entries"]}
    for path,expected in current.items():
        if path in tracked:
            raw = published_bytes(PUBLISHED,path)
        elif path in entries:
            entry = entries[path]
            assert entry["compression"] == "none"
            raw = published_bytes(BASE,entry["source"])
            assert digest(raw) == entry["sha256"] == entry["source_sha256"]
            assert len(raw) == entry["bytes"]
        else:
            raw = preserved_bytes(ROOT,path)
            preflight = json.loads(published_bytes(BASE,"data/processed/literature51_2026_10_16/followup/commit_preflight.json"))
            authority = preflight["reproduction_inputs"][path]
            assert len(raw) == authority["bytes"]
            assert digest(raw) == authority["original_sha256"] == old["source_files_sha256"][path]
        assert digest(raw) == expected,path


def test_all_22_previous_B_artifacts_and_historical_fixtures_remain_byte_exact():
    prior = original()["prior_B1A_K_artifact_sha256"]
    assert len(prior) == 22
    for path,expected in prior.items():
        assert digest(published_bytes(BASE,path)) == digest((ROOT/path).read_bytes()) == expected,path
    for path in baseline_paths("tests/fixtures"):
        assert (ROOT/path).read_bytes() == published_bytes(BASE,path),path


def test_all49_NeurIPS_artifacts_C13_and_separate39_inventory_are_preserved():
    path = "data/raw/systematic_gap_migration_2026_10_03/baseline.json"
    raw = (ROOT/path).read_bytes()
    assert raw == published_bytes(BASE,path)
    frozen = json.loads(raw)["frozen_sha256"]
    assert len(frozen) == 49
    for relative,expected in frozen.items():
        assert digest(preserved_bytes(ROOT,relative)) == expected,relative
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
        assert (ROOT/path).read_bytes() == published_bytes(BASE,path),path


def test_final_report_records_two_acceptances_and_keeps_the_complete_original_report():
    report = (ROOT/REPORT).read_text()
    assert archived_bytes("report").decode() in report
    for token in (*IDS.values(),"R181","R335","PROPOSE_CORRECTION_ACCEPTED","method;dataset","dataset;benchmark",
                  "136,400","9,646","30,000","140","138","127","2025","2026","2027",BASE,
                  "7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA"):
        assert token in report
    assert "unverified" in report.casefold() and "leave-one-out" in report.casefold()
    assert packet()["scope"]["review_decisions_added"] == packet()["scope"]["review_actions_closed"] == 2
    assert packet()["scope"]["authoritative_scientific_changes"] == 2
    assert packet()["scope"]["forensic_task_changes"] == packet()["scope"]["image_scope_changes"] == 0
    assert packet()["scope"]["new_Batch_B_actions_added"] == packet()["scope"]["Batch_B_denominator_changes"] == 0


def test_separate_original_15_boundary_and37_integrity_receipts_are_portable_and_not_conflated_with12_assembly_checks():
    receipts = packet()["evidence_stage_preservation_receipts"]
    expected = {
        "completion-boundary-checks.json":(15,"233f69001da3126bfca1822967a587d880713e1015087211d896c2e367b5b52c"),
        "integrity-final.json":(37,"41491ba7fa11eac9f28aa2bbc93a402ba24b3ffde54bd668149902d61cc54f11"),
    }
    assert set(receipts) == set(expected)
    for name,(passed,sha256) in expected.items():
        entry = receipts[name]
        assert entry["encoding"] == "gzip+base64"
        raw = gzip.decompress(base64.b64decode(entry["gzip_base64"],validate=True))
        assert len(raw) == entry["bytes"] and digest(raw) == entry["sha256"] == sha256
        receipt = json.loads(raw)
        assert receipt == entry["receipt"]
        assert receipt["passed"] == passed and receipt["failed"] == 0
        assert all(c["passed"] is True for c in receipt["checks"])
    assert original()["validation"]["independent_packet_assembly_review"]["passed"] == 12



@pytest.mark.parametrize("rid",["R181","R335"])
def test_live_B1L_selected_rows_public_relationships_and_terminal_prefix_stay_exact(rid):
    """Later approved work may advance totals without changing these accepted cases."""
    pid = TARGETS[rid]
    for path in (PAPERS,TAXONOMY):
        assert selected_row((ROOT/path).read_bytes(),pid) == selected_row(published_bytes(PUBLISHED,path),pid)
    historical,live = published_context(PUBLISHED),load_context()
    assert historical["papers"][pid] == live["papers"][pid]
    assert {key:value for key,value in historical["pairs"].items() if key[0] == pid} == {key:value for key,value in live["pairs"].items() if key[0] == pid}
    before = {row["id"]:row for row in json.loads(published_bytes(PUBLISHED,PUBLIC[1]))["records"] if row.get("paper_id") == pid}
    after = {row["id"]:row for row in json.loads((ROOT/PUBLIC[1]).read_bytes())["records"] if row.get("paper_id") == pid}
    assert before == after and len(before) == {"R181":1,"R335":5}[rid]
    prefix = published_bytes(PUBLISHED,DECISIONS)
    assert (ROOT/DECISIONS).read_bytes().startswith(prefix)
    historical_rows = csv_records(prefix)
    live_rows = read_review_decisions(ROOT/DECISIONS)
    assert live_rows[:len(historical_rows)] == historical_rows
    assert terminal(live_rows)[rid] == IDS[rid]
    assert sum(row["decision_id"] == IDS[rid] for row in live_rows) == 1
