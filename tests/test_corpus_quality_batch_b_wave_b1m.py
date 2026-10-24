"""B1M adds two bounded benchmark contributions without changing their identities."""
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
BASE = "53c2a9aa0fa3a36427ea8e71966e29cdfba70153"
PAPERS = "data/curated/papers.csv"
TAXONOMY = "data/curated/paper_taxonomy.csv"
DECISIONS = "data/curated/review_decisions.csv"
PUBLIC = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
MANIFEST = "data/raw/corpus_quality_batch_b_wave_b1m_2026_10_23/evidence_manifest.json"
REPORT = "docs/corpus_quality_batch_b_wave_b1m_2026_10_23.md"
AUDIT = "data/raw/corpus_quality_audit_2026_10_04/"
FIXTURES = "tests/fixtures/historical_test_fixture_manifest.json"
TARGETS = {"R034":"curated:aa7dceb70828cdd6ad39", "R359":"curated:e688194977fa7bbf7db3"}
FINAL_TYPES = {"R034":["method","dataset","benchmark"], "R359":["method","benchmark"]}
IDS = {"R034":"review:f58480d5cff48573783e", "R359":"review:8613ac0d21d46c5ba17b"}
EVIDENCE_HASHES = {
    "manifest":"9868d49eabab242deb3d6d5811e6b75028d5baf4334b6b1ef074f507cd6022e7",
    "report":"184d4401a7ad9f13a9686189cc8992f6be2f9532604731bcc73adb5ef212d3a4",
}
PDF_HASHES = {"R034":"ee8012fd5021f6ac40f9fc336f81d94e2d734630bface9c333d37cc975e49fe9",
              "R359":"ac331d68d67e6ac2a97bff929ffc410a756bba411a4c1ddfbeb304e593f090c0"}
WORKER_HASHES = {"R034":"b34dbe3d793c30e54be8fb1609e105b942985e37139ee059965b6c693df5b086",
                 "R359":"d18c2e38c7d1fb9e9aa6e1dae3fd090dc99db8436fccb778af62d8ff9ab67770"}
CODE_COMMIT = "9bd6f07db6c220e53d4f2e07ea00bbda761874e3"
CODE_LOCATOR = "https://github.com/nchivar/LAID/blob/" + CODE_COMMIT + "/test.py#L272-L277"
# Frozen exact plan values are inserted here before this draft is delivered.
CSV_UPDATES = {'data/curated/papers.csv': {'R034': {'research_types': 'method;dataset;benchmark'},
                             'R359': {'research_types': 'method;benchmark'}},
 'data/curated/paper_taxonomy.csv': {'R034': {'research_types': 'method;dataset;benchmark',
                                              'research_types_review_reason': 'R034 accepted under '
                                                                              'locked R2: '
                                                                              'RealChain is an '
                                                                              'independently '
                                                                              'specified reusable '
                                                                              'detector-evaluation '
                                                                              'benchmark/protocol/resource, '
                                                                              'distinct from REM '
                                                                              'and its retained '
                                                                              'dataset role. The '
                                                                              'complete ECCV 2026 '
                                                                              'publisher chapter '
                                                                              'defines 7,000 real '
                                                                              'and 7,000 synthetic '
                                                                              'sources, seven '
                                                                              'source/mode strata, '
                                                                              '50 degradation '
                                                                              'chains, ND/CD '
                                                                              'settings, Balanced '
                                                                              'Accuracy and nine '
                                                                              'independent '
                                                                              'baselines. Add '
                                                                              'benchmark; retain '
                                                                              'method, dataset, '
                                                                              'detection and '
                                                                              'fully_generated. '
                                                                              'Contribution '
                                                                              'confidence high; '
                                                                              'reproducibility '
                                                                              'confidence medium. '
                                                                              'Complete chain '
                                                                              'definitions, '
                                                                              'timed-out JSON, '
                                                                              'archive contents, '
                                                                              'splits, evaluator '
                                                                              'and numerical '
                                                                              'reproduction remain '
                                                                              'unverified. '
                                                                              'Preserve nonuniform '
                                                                              'REM superiority, '
                                                                              'DRCT table '
                                                                              'discrepancies, '
                                                                              'backbone/average '
                                                                              'ambiguity and CDC '
                                                                              'ablation '
                                                                              'inconsistency. '
                                                                              'OUT_OF_SCOPE_BIBLIOGRAPHIC_VERSION_OBSERVATION '
                                                                              'remains separate; '
                                                                              'P034 and all '
                                                                              'canonical '
                                                                              'bibliographic '
                                                                              'fields remain '
                                                                              'pending and '
                                                                              'unchanged.',
                                              'research_types_evidence_tier': 'primary_paper',
                                              'research_types_evidence_source': 'https://link.springer.com/content/pdf/10.1007/978-3-032-37429-5_14.pdf',
                                              'research_types_evidence_excerpt': 'ECCV publisher '
                                                                                 'DOI '
                                                                                 '10.1007/978-3-032-37429-5_14, '
                                                                                 'sections 4-5, '
                                                                                 'Tables 1 and 5: '
                                                                                 'RealChain ND/CD '
                                                                                 'Balanced '
                                                                                 'Accuracy REM '
                                                                                 '92.4/84.2 versus '
                                                                                 'DDA 88.8/65.8; '
                                                                                 'CD gap 18.4 '
                                                                                 'percentage '
                                                                                 'points. The '
                                                                                 'benchmark has '
                                                                                 '7,000 real plus '
                                                                                 '7,000 synthetic '
                                                                                 'source images, '
                                                                                 'seven '
                                                                                 'source/mode '
                                                                                 'strata, 50 '
                                                                                 'chains each '
                                                                                 'processing 140 '
                                                                                 'real and 140 '
                                                                                 'fake, and nine '
                                                                                 'independent '
                                                                                 'baselines. Not a '
                                                                                 '50-times-full-corpus '
                                                                                 'cross product. '
                                                                                 'Full chain '
                                                                                 'configuration/splits/archive/evaluator '
                                                                                 'and independent '
                                                                                 'reproduction '
                                                                                 'unverified; '
                                                                                 'timed-out JSON '
                                                                                 'preserved. Git '
                                                                                 'c1e8aacf68f041d3abe6509dc01425c5e42ab01e; '
                                                                                 'HF '
                                                                                 '0f0007d05cbd5ab6213783ad9ec3c2d38ab457c0. '
                                                                                 'Bibliographic '
                                                                                 'version '
                                                                                 'differences '
                                                                                 'remain outside '
                                                                                 'this R2 '
                                                                                 'correction; P034 '
                                                                                 'pending.',
                                              'audited_at': '2026-10-23'},
                                     'R359': {'research_types': 'method;benchmark',
                                              'research_types_review_reason': 'R359 accepted under '
                                                                              'locked R2: LAID '
                                                                              'contributes a '
                                                                              'separately intended '
                                                                              'model-independent '
                                                                              'comparative '
                                                                              'framework with '
                                                                              'architecture '
                                                                              'eligibility/resource '
                                                                              'constraints, '
                                                                              'reusable '
                                                                              'training/testing '
                                                                              'interfaces, '
                                                                              'spatial/FFT inputs, '
                                                                              'standardized '
                                                                              'recipes, GenImage '
                                                                              'sampling, joint '
                                                                              'accuracy/resource '
                                                                              'measures and '
                                                                              'controlled '
                                                                              'postprocessing '
                                                                              'evaluations. This '
                                                                              'exceeds ordinary '
                                                                              'model selection and '
                                                                              'differs from '
                                                                              'bounded R215; model '
                                                                              'count alone is '
                                                                              'insufficient. Add '
                                                                              'benchmark; retain '
                                                                              'method, detection '
                                                                              'and '
                                                                              'fully_generated; no '
                                                                              'dataset or '
                                                                              'analysis_study. '
                                                                              'Medium contribution '
                                                                              'confidence. Oracle '
                                                                              'Fusion Accuracy is '
                                                                              'label-dependent '
                                                                              'correctness union, '
                                                                              'not a deployable '
                                                                              'predicted class; '
                                                                              'maximum-probability '
                                                                              'score metrics are '
                                                                              'separate. The '
                                                                              'reported 65.09% '
                                                                              'spatial versus '
                                                                              '90.91% oracle '
                                                                              'fusion is not an '
                                                                              'established '
                                                                              'practical fusion '
                                                                              'improvement. Pinned '
                                                                              'test.py confirms '
                                                                              'the rule, not Table '
                                                                              'III numerical '
                                                                              'reproduction. '
                                                                              'Preserve '
                                                                              'publisher-final/code-version, '
                                                                              'checkpoints/splits, '
                                                                              'OR/AND, training, '
                                                                              'perturbation, '
                                                                              'generalization, '
                                                                              'resource and '
                                                                              'correlation '
                                                                              'limitations.',
                                              'research_types_evidence_tier': 'primary_paper',
                                              'research_types_evidence_source': 'https://arxiv.org/pdf/2507.05162v1',
                                              'research_types_evidence_excerpt': 'arXiv '
                                                                                 '2507.05162v1: '
                                                                                 'ten generic '
                                                                                 'architectures '
                                                                                 'and two '
                                                                                 'baselines, '
                                                                                 '100,000/16,000/16,000 '
                                                                                 'training/validation/test '
                                                                                 'images, '
                                                                                 'spatial/FFT '
                                                                                 'models and '
                                                                                 'accuracy/resource/postprocessing '
                                                                                 'comparisons. '
                                                                                 'Clean '
                                                                                 'spatial/spectral '
                                                                                 'accuracy '
                                                                                 'percentages: '
                                                                                 'MobileViT '
                                                                                 '97.17/99.89; '
                                                                                 'FastViT '
                                                                                 '98.87/99.91; '
                                                                                 'MnasNet '
                                                                                 '78.11/50.36. '
                                                                                 'Pinned '
                                                                                 'https://github.com/nchivar/LAID/blob/9bd6f07db6c220e53d4f2e07ea00bbda761874e3/test.py#L272-L277 '
                                                                                 'uses '
                                                                                 'ground-truth '
                                                                                 'correctness OR '
                                                                                 'for fusion '
                                                                                 'accuracy; max '
                                                                                 'fake probability '
                                                                                 'separately '
                                                                                 'supplies score '
                                                                                 'metrics. FastViT '
                                                                                 'combined '
                                                                                 'perturbation '
                                                                                 'spatial 65.09% '
                                                                                 'versus Oracle '
                                                                                 'Fusion Accuracy '
                                                                                 '90.91% is not '
                                                                                 'deployable '
                                                                                 'fusion accuracy. '
                                                                                 'Code-rule '
                                                                                 'verification is '
                                                                                 'not reproduction '
                                                                                 'of Table III. '
                                                                                 'Publisher-final, '
                                                                                 'paper-time code, '
                                                                                 'full '
                                                                                 'checkpoints/splits '
                                                                                 'and exact '
                                                                                 'reproduction '
                                                                                 'remain '
                                                                                 'unverified.',
                                              'audited_at': '2026-10-23'}}}
CSV_AFTER_HASHES = {'data/curated/papers.csv': '5a7dab97bdd2c0728aba3f88a2fe8756208e341b974dcdff8ce2f79869ee7fa7',
 'data/curated/paper_taxonomy.csv': '81ce6b101b34645f6b360ba5542036b72419830a72800cff2a2e2b8fa09fae0b'}


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
    entry = packet()["evidence_only_packet_archives"][kind]
    raw = decode_archive(entry)
    assert digest(raw) == EVIDENCE_HASHES[kind]
    return raw


@lru_cache
def original():
    return json.loads(archived_bytes("manifest"))


def record(data, rid):
    found = [r for r in data["records"] if r["review_id"] == rid]
    assert len(found) == 1
    return found[0]


def science(rid):
    row = record(packet(), rid)
    return row["scientific_review"] if rid == "R034" else row


def selected_row(raw, pid):
    rows = [r for r in csv_records(raw) if r["paper_id"] == pid]
    assert len(rows) == 1
    return rows[0]


def terminal(rows):
    result = {}
    for row in rows:
        match = re.search(r"\bBatch B review ([A-Z]\d{3});", row["review_note"])
        if match and row["action"] == "no_action_after_review":
            assert match[1] not in result, "Duplicate terminal original review"
            result[match[1]] = row["decision_id"]
    return result


def accounting(rows, public):
    ledger = [r for r in decision_rows(load_queues()) if r["batch"] == "B"]
    done = terminal(rows)
    pending = [r for r in ledger if r["review_id"] not in done]
    active = [r for r in pending if r["paper_id"] in public]
    return {
        "historical_actions":len(ledger), "historical_papers":len({r["paper_id"] for r in ledger}),
        "closed_review_ids":sorted(done),
        "historical_unresolved_actions":len(pending), "historical_unresolved_papers":len({r["paper_id"] for r in pending}),
        "active_public_unresolved_actions":len(active), "active_public_unresolved_papers":len({r["paper_id"] for r in active}),
        "historical_unresolved_review_ids":[r["review_id"] for r in pending],
        "active_public_unresolved_review_ids":[r["review_id"] for r in active],
    }


@lru_cache
def baseline_paths(*prefixes):
    return subprocess.check_output(["git","--no-optional-locks","ls-tree","-r","--name-only",BASE,"--",*prefixes],cwd=ROOT,text=True).splitlines()


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
    """Quote only approved cells while retaining every unrelated CSV token."""
    spans, start, i, quoted = [], 0, 0, False
    while i < len(raw):
        byte = raw[i]
        if byte == 34:
            if quoted and i + 1 < len(raw) and raw[i + 1] == 34:
                i += 2
                continue
            quoted = not quoted
        elif not quoted and byte == 44:
            spans.append((start,i)); start = i + 1
        elif not quoted and byte in (10,13):
            spans.append((start,i)); break
        i += 1
    else:
        spans.append((start,len(raw)))
    assert not quoted and len(spans) == len(header)
    edits = []
    for field,value in updates.items():
        stream = io.StringIO(newline="")
        csv.writer(stream,lineterminator="\n").writerow([value])
        edits.append((*spans[header.index(field)],stream.getvalue()[:-1].encode()))
    for begin,end,token in sorted(edits,reverse=True):
        raw = raw[:begin] + token + raw[end:]
    return raw


@pytest.mark.parametrize("kind",["manifest","report"])
def test_evidence_only_packet_is_losslessly_preserved_and_portable(kind):
    assert archived_bytes(kind)
    assert set(packet()["evidence_only_packet_archives"]) == {"manifest","report"}
    assert original()["baseline_commit"] == packet()["baseline_commit"] == BASE
    assert original()["scope"]["authoritative_data_changes"] == original()["scope"]["review_actions_closed"] == 0


def test_complete_original_science_and_timestamps_survive_only_outer_acceptance_flags_change():
    old,new = original(),packet()
    assert [r["review_id"] for r in new["records"]] == list(TARGETS)
    flags = {"maintainer_acceptance_pending","review_closed","authoritative_changes_applied","terminal_review_decision_created"}
    for rid in TARGETS:
        before,after = record(old,rid),record(new,rid)
        assert {k:after[k] for k in before if k not in flags} == {k:v for k,v in before.items() if k not in flags}
        assert after["maintainer_acceptance_pending"] is False
        assert all(after[k] is True for k in flags-{"maintainer_acceptance_pending"})
        assert after["accepted_outcome"] == "PROPOSE_CORRECTION_ACCEPTED"
        assert after["terminal_review_decision_id"] == IDS[rid]
        assert after["final_authoritative_taxonomy"] == {"tasks":["detection"],"image_scopes":["fully_generated"],"research_types":FINAL_TYPES[rid]}
    mutable = {"phase","scope","validation","integrity","corpus_counts","taxonomy_counts","batch_b_accounting","git_requirements"}
    for key in old:
        if key not in mutable|{"records"}:
            assert new[key] == old[key],key
    for key in mutable:
        assert new["evidence_only_"+key] == old[key],key


def test_original_worker_receipts_and_full_worker_bytes_are_authenticated_without_TMP_dependencies():
    old = original()
    for rid,count in (("R034",57),("R359",59)):
        receipt = old["worker_validation"][rid]["receipt"]
        assert receipt["passed"] == count and receipt["failed"] == 0
        assert all(x["passed"] for x in receipt["checks"])
        archive = old["complete_worker_artifact_archives"][rid]["review.json"]
        assert digest(decode_archive(archive)) == WORKER_HASHES[rid]
        for name,entry in old["complete_worker_artifact_archives"][rid].items():
            raw = decode_archive(entry)
            if name in receipt["artifact_sha256"]:
                assert digest(raw) == receipt["artifact_sha256"][name]
    receipts = old["independent_review_findings"]
    for name,count in (("independent-source-provenance.json",21),("r034-independent-release-provenance.json",10),("independent-scientific-crossreview.json",76)):
        assert receipts[name]["receipt"]["passed"] == count and receipts[name]["receipt"]["failed"] == 0
    assert old["validation"]["independent_packet_assembly_review"]["passed"] == 23
    assert old["validation"]["final_preservation_receipt"]["passed"] == 39


@pytest.mark.parametrize("path",[PAPERS,TAXONOMY])
def test_exact_two_rows_per_CSV_and_fourteen_cells_change_with_all_other_tokens_identical(path):
    old_raw,new_raw = published_bytes(BASE,path),(ROOT/path).read_bytes()
    old,new = csv_records(old_raw),csv_records(new_raw)
    identity = "taxonomy_id" if path == TAXONOMY else "paper_id"
    assert [r[identity] for r in old] == [r[identity] for r in new]
    assert {r["paper_id"] for r,s in zip(old,new) if r != s} == set(TARGETS.values())
    for rid,pid in TARGETS.items():
        before,after = selected_row(old_raw,pid),selected_row(new_raw,pid)
        updates = CSV_UPDATES[path][rid]
        assert after == {**before,**updates}
        assert {k for k in before if before[k] != after[k]} == updates.keys()
        assert after["research_types"] == ";".join(FINAL_TYPES[rid])
        assert before["tasks"] == after["tasks"] == "detection"
        assert before["image_scopes"] == after["image_scopes"] == "fully_generated"
        if path == PAPERS:
            assert set(updates) == {"research_types"}
        else:
            assert set(updates) == {"research_types","research_types_review_reason","research_types_evidence_tier","research_types_evidence_source","research_types_evidence_excerpt","audited_at"}
            assert after["research_types_status"] == before["research_types_status"] == "reviewed"
            assert after["research_types_evidence_tier"] == "primary_paper"
            assert after["research_types_evidence_source"] == record(original(),rid)["source"]["url"]
    header = next(csv.reader(io.StringIO(old_raw.decode(),newline="")))
    chunks = logical_csv_chunks(old_raw)
    targets = {pid:rid for rid,pid in TARGETS.items()}
    expected = [chunks[0]]
    for row,chunk in zip(old,chunks[1:]):
        rid = targets.get(row["paper_id"])
        expected.append(replace_csv_tokens(chunk,header,CSV_UPDATES[path][rid]) if rid else chunk)
    assert new_raw == b"".join(expected)
    assert digest(new_raw) == CSV_AFTER_HASHES[path]


def test_exact_two_terminal_appends_preserve_all_94_prior_rows_and_their_bytes():
    before,after = published_bytes(BASE,DECISIONS),(ROOT/DECISIONS).read_bytes()
    prior,rows = csv_records(before),read_review_decisions(ROOT/DECISIONS)
    assert after.startswith(before) and len(prior) == 94 and len(rows) == 96
    assert rows[:-2] == prior and len({r["decision_id"] for r in rows}) == 96
    assert terminal(rows) == {**terminal(prior),**IDS}
    assert [r["decision_id"] for r in rows[-2:]] == list(IDS.values())
    for rid,row in zip(TARGETS,rows[-2:]):
        assert row["decision_id"] == IDS[rid]
        assert row["review_queue"] == "other" and row["review_queue"] in ALLOWED_REVIEW_QUEUES
        assert row["action"] == "no_action_after_review" and row["action"] in ALLOWED_REVIEW_ACTIONS
        assert row["target_type"] == "paper" and row["institution"] == ""
        assert row["created_by"] == "maintainer-approved-batch-b-b1m"
        assert row["created_at"] == row["updated_at"]
        assert datetime.fromisoformat(row["created_at"].replace("Z","+00:00")).tzinfo == timezone.utc
        original_paper = selected_row(published_bytes(BASE,PAPERS),TARGETS[rid])
        assert all(row[k] == original_paper[k] for k in ("title","year","doi","openalex_url"))
        identity = "|".join(" ".join(row[k].split()).casefold() for k in ("review_queue","target_type","doi","openalex_url","title","year","institution"))
        assert "review:"+digest(identity.encode())[:20] == IDS[rid]
        assert row["review_note"].startswith("Batch B review "+rid+";")
        assert all(x in row["review_note"] for x in ("PROPOSE_CORRECTION_ACCEPTED","R2",PDF_HASHES[rid]))
        if rid == "R359":
            assert all(x in row["review_note"] for x in (CODE_LOCATOR,"Oracle","65.09","90.91","not deployable"))
        assert packet()["adjudication"]["terminal_decisions"][rid] == row
    transaction = packet()["adjudication"]
    assert transaction["decision_ids"] == IDS
    assert transaction["registry_rows_before"] == 94 and transaction["registry_rows_after"] == 96
    assert transaction["before_registry_sha256"] == digest(before) and transaction["after_registry_sha256"] == digest(after)
    assert transaction["prior_decision_bytes_preserved"] is True
    assert transaction["existing_csv_cells_changed"] == 14 and len(transaction["csv_changes"]) == 4
    for edit in transaction["csv_changes"]:
        rid = next(r for r,pid in TARGETS.items() if pid == edit["row_identity"]["paper_id"])
        assert edit["after_fields"] == CSV_UPDATES[edit["path"]][rid]
        assert edit["planned_after_sha256"] == CSV_AFTER_HASHES[edit["path"]]


@pytest.mark.parametrize("rid",list(TARGETS))
def test_terminal_upsert_has_no_byte_or_timestamp_churn(tmp_path,rid):
    path = tmp_path/"review_decisions.csv"
    raw = (ROOT/DECISIONS).read_bytes()
    path.write_bytes(raw)
    row = next(r for r in read_review_decisions(path) if r["decision_id"] == IDS[rid])
    assert upsert_review_decision(row,path=path) == row
    assert path.read_bytes() == raw


def test_only_two_research_type_actions_close_and_P034_keeps_its_paper_unresolved():
    before = accounting(csv_records(published_bytes(BASE,DECISIONS)),published_context(BASE)["papers"])
    after = accounting(read_review_decisions(ROOT/DECISIONS),load_context()["papers"])
    assert after == packet()["batch_b_accounting"]
    fields = ("historical_actions","historical_papers","historical_unresolved_actions","historical_unresolved_papers","active_public_unresolved_actions","active_public_unresolved_papers")
    assert [before[k] for k in fields] == [159,148,140,129,138,127]
    assert [after[k] for k in fields] == [159,148,138,128,136,126]
    assert set(after["closed_review_ids"])-set(before["closed_review_ids"]) == set(TARGETS)
    for name in ("historical_unresolved_review_ids","active_public_unresolved_review_ids"):
        assert after[name] == [r for r in before[name] if r not in TARGETS]
        assert "P034" in after[name]
    assert "P034" not in terminal(read_review_decisions(ROOT/DECISIONS))
    ledger = [r for r in decision_rows(load_queues()) if r["batch"] == "B"]
    assert {r["review_id"] for r in ledger if r["paper_id"] == TARGETS["R034"]} == {"R034","P034"}
    assert {r["review_id"] for r in ledger if r["paper_id"] == TARGETS["R359"]} == {"R359"}


@pytest.mark.parametrize("rid,pages,size",[("R034",19,3126434),("R359",10,1502619)])
def test_complete_primary_versions_hashes_and_limits_are_retained(rid,pages,size):
    source = record(packet(),rid)["source"]
    assert source["sha256"] == PDF_HASHES[rid] and source["bytes"] == size and source["pages"] == pages
    assert source["full_manuscript_read"] is True and source["pages_read"] == list(range(1,pages+1))
    if rid == "R034":
        assert source["doi"] == "10.1007/978-3-032-37429-5_14" and len(source["authors"]) == 13
        assert source["arxiv_full_manuscript_obtained"] is source["supplement_retrieved"] is False
    else:
        assert source["url"] == "https://arxiv.org/pdf/2507.05162v1"
        assert source["publication_final_equivalence_verified"] is False


def test_RealChain_independent_ND_CD_protocol_counts_and_metrics_support_R2_without_a_full_cross_product():
    r = science("R034")
    p = r["RealChain_protocol"]
    assert (p["real_images"],p["synthetic_images"],p["clean_source_images"]) == (7000,7000,14000)
    assert (p["text_to_image_images"],p["image_to_image_images"],p["distinct_generator_families"],p["source_mode_strata"]) == (6000,1000,6,7)
    assert p["chains_claimed"] == 50 and p["main_paper_chain_examples_shown"] == 20
    assert (p["real_per_chain"],p["fake_per_chain"],p["implied_final_CD_instances"]) == (140,140,14000)
    assert p["full_50_by_14000_cross_product_claimed"] is False
    assert (p["propagation_operations_per_chain_min"],p["propagation_operations_per_chain_max"],p["postprocessing_operations_per_chain_min"],p["postprocessing_operations_per_chain_max"]) == (1,3,0,2)
    assert len(r["evaluation_protocol"]["independent_baselines"]) == 9
    result = r["key_numerical_results"]["RealChain"]
    assert [result[k] for k in ("REM_ND","REM_CD","DDA_ND","DDA_CD","CD_difference_percentage_points")] == [92.4,84.2,88.8,65.8,18.4]
    assert r["policy_assessment"]["locked_policy"]["policy_id"] == "R2"
    assert r["policy_assessment"]["scientific_contribution_confidence"] == "high"
    assert r["policy_assessment"]["operational_reproducibility_confidence"] == "medium"


def test_RealChain_numeric_counterexamples_and_unverified_release_do_not_disappear_after_acceptance():
    r = science("R034")
    tables = {x["table"]:x for x in r["quantitative_evidence"]["tables"]}
    assert r["quantitative_evidence"]["numeric_result_cells"] == 810
    def cell(t,method,key):
        return next(x["balanced_accuracy_percent"][key] for x in tables[t]["rows"] if x.get("method",x.get("backbone")) == method)
    assert cell(1,"REM","ForenSynths") == "91.5" and cell(1,"C2P-CLIP","ForenSynths") == "92.0"
    assert cell(1,"DRCT","RealChain_ND") == "69.1" and cell(5,"DRCT","Avg_ND") == "68.6"
    assert cell(8,"DINOv3-H+/16","Avg") == "93.6" and cell(8,"DINOv3-7B/16","Avg") == "94.9"
    assert len(r["counterevidence_and_inconsistencies"]) == 6
    release = r["release_review"]
    assert release["repository_commit"] == "c1e8aacf68f041d3abe6509dc01425c5e42ab01e"
    assert release["Hugging_Face_revision"] == "0f0007d05cbd5ab6213783ad9ec3c2d38ab457c0"
    assert release["complete_release_verified"] is release["publisher_final_release_equivalence_verified"] is False
    assert release["training_inference_code_verified_available"] is release["Hugging_Face_card_or_license_verified"] is False
    failure = release["chain_configuration_access"]
    assert (failure["HTTP"],failure["curl_exit_code"],failure["body_bytes"],failure["retries"]) == (0,28,0,0)
    assert failure["body_sha256"] is None
    assert r["RealChain_protocol"]["fixed_file_splits_verified"] is r["RealChain_protocol"]["source_content_disjointness_verified"] is False


def test_R034_version_observation_stays_separate_from_pending_P034_and_live_bibliographic_identity():
    observation = science("R034")["out_of_scope_bibliographic_version_observation"]
    assert observation["marker"] == "OUT_OF_SCOPE_BIBLIOGRAPHIC_VERSION_OBSERVATION"
    early,publisher = observation["early_arxiv"],observation["publisher"]
    assert (early["author_count"],early["abstract_benchmark_evaluations"],early["abstract_average_improvement_percent"]) == (12,8,7.5)
    assert (publisher["author_count"],publisher["abstract_benchmark_evaluations"],publisher["abstract_average_improvement_percent"]) == (13,12,6.9)
    assert publisher["authors"][7] == "Manni Cui" and early["full_manuscript_obtained_or_read"] is False
    assert observation["P034_remains_pending"] is True and observation["canonical_metadata_changed"] is observation["new_review_action_created"] is False
    before = selected_row(published_bytes(BASE,PAPERS),TARGETS["R034"])
    after = selected_row((ROOT/PAPERS).read_bytes(),TARGETS["R034"])
    assert after == {**before,"research_types":"method;dataset;benchmark"}
    assert after["doi"] == "" and len(after["authors"].split(";")) == 12
    queues = load_queues()
    assert (ROOT/(AUDIT+"publication_metadata_review.json")).read_bytes() == published_bytes(BASE,AUDIT+"publication_metadata_review.json")
    assert record(packet(),"R034")["independent_pending_original_B_actions"] == record(original(),"R034")["independent_pending_original_B_actions"]


def test_LAID_framework_is_model_independent_not_a_new_dataset_or_only_model_count():
    r = science("R359")
    p = r["protocol"]
    assert p["data"]["existing_resource"] == "GenImage reused; no new dataset claim"
    assert p["data"]["paper_sample_counts"] == {"train":100000,"validation":16000,"test":16000}
    assert len(r["quantitative_tables"]["Table I"]["rows"]) == 10
    assert len(r["quantitative_tables"]["Table II"]["rows"]) == 12
    assert p["paper_training"]["batch_size"] == 512 and p["paper_training"]["learning_rate"] == "1e-4"
    assert p["representations"]["spatial"] and p["representations"]["spectral"]
    assert "R215" in r["R2_assessment"]["precedent_boundaries"]
    assert r["R2_assessment"]["competing_interpretation"]
    assert "Medium" in r["confidence"]["R2_benchmark_contribution"]
    accepted_reason = CSV_UPDATES[TAXONOMY]["R359"]["research_types_review_reason"]
    assert all(x in accepted_reason for x in ("model-independent","interfaces","resource","R215","model count alone is insufficient"))
    assert FINAL_TYPES["R359"] == ["method","benchmark"]


def test_LAID_clean_metrics_and_ordinary_robustness_are_separate_from_oracle_fusion():
    r = science("R359")
    tables = r["quantitative_tables"]
    clean = {row["model"]:row["values"] for row in tables["Table II"]["rows"]}
    assert [(clean[m][0],clean[m][3]) for m in ("MobileViT","FastViT","MnasNet")] == [("97.17","99.89"),("98.87","99.91"),("78.11","50.36")]
    perturbed = tables["Table III"]["settings"]
    def combined(setting):
        return next(x["values"][-1] for x in perturbed[setting]["rows"] if x["model"] == "FastViT")
    assert combined("spatial") == "65.09" and combined("fusion_oracle_correctness_union") == "90.91"
    assert combined("spectral") == "50.22"
    assert "50% probability" in r["protocol"]["perturbations"]["combined"]
    assert "not gradient-based" in r["protocol"]["perturbations"]["threat_model"]
    assert "future work" in r["protocol"]["data"]["generator_holdout"]


def test_pinned_label_dependent_oracle_is_explicit_and_not_approved_as_deployable_accuracy():
    qualification = packet()["R359_oracle_fusion_qualification"]
    assert qualification["classification"] == "ORACLE_CORRECTNESS_UNION"
    assert qualification["code_url"] == CODE_LOCATOR and qualification["repository_commit"] == CODE_COMMIT
    assert qualification["file"] == "test.py" and qualification["function"] == "test_attacked"
    assert qualification["line_range"] == [272,277]
    assert qualification["accuracy_expression"] == "(img_preds[i] == labels[i]) or (freq_preds[i] == labels[i])"
    assert qualification["label_dependent"] is True
    assert qualification["deployable_fusion_accuracy_validated"] is qualification["independent_numerical_reproduction"] is False
    assert qualification["separate_score_rule"] == "maximum fake probability" and qualification["score_metrics"] == ["F1","AUROC"]
    assert qualification["FastViT_combined"] == {"spatial_accuracy_percent":65.09,"oracle_fusion_accuracy_percent":90.91,"practical_fusion_improvement_established":False}
    fusion = science("R359")["fusion_implementation_review"]
    assert fusion["pinned_repository_commit"] == CODE_COMMIT
    assert fusion["source_body_sha256"] == "f65d26cc6b789a64204e0e3629177b41ddef48b86199951f234e966fde3f5e92"
    assert fusion["source_read_only"] is True and fusion["source_execution"] is False
    assert len(fusion["questions"]) == 10 and "not an execution" in fusion["questions"][7]["answer"]


def test_LAID_source_time_and_reproduction_restrictions_are_not_silently_resolved():
    r = science("R359")
    assert r["source"]["publication_final_equivalence_verified"] is False
    assert r["release_review"]["pinned_commit"] == CODE_COMMIT
    assert r["release_review"]["commit_committer_date"] == "2025-12-01T05:05:43Z"
    assert "unverified" in r["release_review"]["reproduction_status"] or "No code executed" in r["release_review"]["reproduction_status"]
    assert "CrossEntropyLoss" in r["protocol"]["code_training_differences"]["loss"]
    assert "val_loss" in r["protocol"]["code_training_differences"]["checkpoint"]
    assert "OR" in r["protocol"]["model_selection"]["eligibility"] and "AND" in r["protocol"]["model_selection"]["eligibility"]
    assert r["counterevidence_and_limits"]
    assert r["release_review"]["license"]["LICENSE_file_in_tree"] is False


def test_original_two_manuscripts_and_no_post_recovery_or_adjudication_downloads():
    retrieval = packet()["retrieval_accounting"]
    assert retrieval == original()["retrieval_accounting"]
    assert retrieval["new_complete_manuscripts_by_review"] == {"R034":1,"R359":1}
    assert retrieval["new_complete_manuscripts_total"] == retrieval["complete_distinct_manuscripts_reviewed_total"] == 2
    assert retrieval["new_full_manuscript_transfers_after_resume"] == retrieval["successful_complete_downloads_repeated"] == 0


def test_exact_two_public_papers_and_eight_existing_map_rows_change_only_types_and_reason():
    old,live = published_context(BASE),load_context()
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
        before,after = json.loads(published_bytes(BASE,path)),json.loads((ROOT/path).read_bytes())
        oldmeta,newmeta = deepcopy(before["metadata"]),deepcopy(after["metadata"])
        oldmeta.pop("public_preview_generated_at",None); newmeta.pop("public_preview_generated_at",None)
        assert oldmeta == newmeta
        assert {k:v for k,v in before.items() if k not in {"records","metadata"}} == {k:v for k,v in after.items() if k not in {"records","metadata"}}
    before = {r["id"]:r for r in json.loads(published_bytes(BASE,PUBLIC[1]))["records"]}
    after = {r["id"]:r for r in json.loads((ROOT/PUBLIC[1]).read_bytes())["records"]}
    assert before.keys() == after.keys() and len(after) == 1410
    dependents = {rid:{key for key,row in before.items() if row.get("paper_id") == pid} for rid,pid in TARGETS.items()}
    assert {rid:len(ids) for rid,ids in dependents.items()} == {"R034":7,"R359":1}
    target_ids = set.union(*dependents.values())
    assert {key for key in before if before[key] != after[key]} == target_ids
    assert sum(before[k] == after[k] for k in before if k not in target_ids) == 1402
    by_paper = {pid:rid for rid,pid in TARGETS.items()}
    for key,row in before.items():
        expected = deepcopy(row)
        rid = by_paper.get(row.get("paper_id"))
        if rid:
            expected["research_types"] = FINAL_TYPES[rid]
            expected["taxonomy_review"]["research_types"]["reason"] = CSV_UPDATES[TAXONOMY][rid]["research_types_review_reason"]
        assert after[key] == expected,key


def test_recomputed_corpus_task_and_type_counts_change_only_two_benchmarks():
    old,live = published_context(BASE),load_context()
    assert old["counts"] == live["counts"] == packet()["corpus_counts"] == CURRENT_CORPUS_COUNTS
    def totals(context):
        return Counter(label for row in context["papers"].values() for dimension in ("tasks","research_types") for label in row[dimension])
    before,after = totals(old),totals(live)
    assert not before-after and after-before == {"benchmark":2}
    assert before["benchmark"] == 91 and after["benchmark"] == 93
    assert after == packet()["taxonomy_counts"] == CURRENT_TAXONOMY_TOTALS
    assert after == {"detection":621,"source_attribution":84,"localization":45,"method":578,"dataset":137,"benchmark":93,"survey":21,"analysis_study":82}


def test_original_questions_locked_R2_and_all_unrelated_authoritative_files_remain_unchanged():
    rows = {r["review_id"]:r for r in load_queues()["taxonomy_review"]["records"]}
    for rid in TARGETS:
        assert record(packet(),rid)["original_review"] == rows[rid]
    policy = json.loads((ROOT/(AUDIT+"batch_c_policy_decisions.json")).read_bytes())
    r2 = next(r for r in policy["policies"] if r["policy_id"] == "R2")
    assert packet()["locked_policy_ledger"]["policies"] == [r2]
    assert "Large experimental tables" in r2["final_rule"]
    allowed = {PAPERS,TAXONOMY,DECISIONS,*PUBLIC}
    for path in baseline_paths("data/curated","data/manual","web/data"):
        if path not in allowed:
            assert (ROOT/path).read_bytes() == published_bytes(BASE,path),path
    for name in ("taxonomy_review","publication_metadata_review","relationship_review","unmapped_papers","batch_c_policy_decisions"):
        path = AUDIT+name+".json"
        assert (ROOT/path).read_bytes() == published_bytes(BASE,path),path


def test_portable_source_authorities_bind_exactly_five_changed_dependencies():
    old,new = original(),packet()
    assert new["source_files_sha256"] == old["source_files_sha256"]
    current = new["current_source_sha256"]
    assert current.keys() == old["source_files_sha256"].keys()
    assert {p for p in current if current[p] != old["source_files_sha256"][p]} == {PAPERS,TAXONOMY,DECISIONS,*PUBLIC}
    tracked = set(baseline_paths())
    fixtures = {r["path"]:r for r in json.loads(published_bytes(BASE,FIXTURES))["entries"]}
    for path,expected in current.items():
        if path in tracked:
            raw = (ROOT/path).read_bytes()
        elif path in fixtures:
            entry = fixtures[path]
            assert entry["compression"] == "none"
            raw = published_bytes(BASE,entry["source"])
            assert len(raw) == entry["bytes"] and digest(raw) == entry["sha256"] == entry["source_sha256"]
        else:
            raw = preserved_bytes(ROOT,path)
            preflight = json.loads(published_bytes(BASE,"data/processed/literature51_2026_10_16/followup/commit_preflight.json"))
            authority = preflight["reproduction_inputs"][path]
            assert len(raw) == authority["bytes"] and digest(raw) == authority["original_sha256"] == old["source_files_sha256"][path]
        assert digest(raw) == expected,path


def test_previous_24_packets_fixtures_frozen49_C13_and_separate39_are_immutable():
    prior = original()["prior_B1A_L_artifact_sha256"]
    assert len(prior) == 24
    for path,expected in prior.items():
        assert digest(published_bytes(BASE,path)) == digest((ROOT/path).read_bytes()) == expected,path
    for path in baseline_paths("tests/fixtures"):
        assert (ROOT/path).read_bytes() == published_bytes(BASE,path),path
    path = "data/raw/systematic_gap_migration_2026_10_03/baseline.json"
    raw = (ROOT/path).read_bytes()
    assert raw == published_bytes(BASE,path)
    frozen = json.loads(raw)["frozen_sha256"]
    assert len(frozen) == 49
    for path,expected in frozen.items():
        assert digest(preserved_bytes(ROOT,path)) == expected,path
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


def test_original_39_preservation_and25_completion_receipts_remain_separate_portable_evidence():
    entries = packet()["evidence_stage_preservation_receipts"]
    assert set(entries) == {"integrity-final.json","completion-boundary-checks.json"}
    for name,count in (("integrity-final.json",39),("completion-boundary-checks.json",25)):
        entry = entries[name]
        receipt = json.loads(decode_archive(entry))
        assert receipt == entry["receipt"]
        assert receipt["passed"] == count and receipt["failed"] == 0
        assert all(x["passed"] for x in receipt["checks"])
    assert original()["validation"]["independent_packet_assembly_review"]["passed"] == 23


def test_final_report_keeps_original_evidence_and_acceptance_qualifications_prominent():
    report = (ROOT/REPORT).read_text()
    assert archived_bytes("report").decode() in report
    for token in (*IDS.values(),"R034","R359","PROPOSE_CORRECTION_ACCEPTED","method;dataset;benchmark","method;benchmark",CODE_LOCATOR,"65.09","90.91","P034","OUT_OF_SCOPE_BIBLIOGRAPHIC_VERSION_OBSERVATION",BASE):
        assert token in report
    assert "Oracle Fusion Accuracy" in report and "label-dependent" in report and "not" in report
    assert packet()["scope"]["review_decisions_added"] == packet()["scope"]["review_actions_closed"] == 2
    assert packet()["scope"]["authoritative_scientific_changes"] == 2
    for key in ("forensic_task_changes","image_scope_changes","publication_metadata_changes","new_Batch_B_actions_added","Batch_B_denominator_changes"):
        assert packet()["scope"][key] == 0
