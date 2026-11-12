"""Verify the B5-04 authoritative transaction and its exact public projection."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import csv
import hashlib
import io
import json
import re
import subprocess

import pytest

from scripts.curated_export import PaperIdentityCache, PaperIdentityIndex
from scripts.validate_corpus_quality_audit import decision_rows, load_queues

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "db1abff06d9ee077ae62421079059ee3af95607f"
PAPERS = "data/curated/papers.csv"
MAPPINGS = "data/curated/author_institution_mappings.csv"
DECISIONS = "data/curated/review_decisions.csv"
LOCATIONS = "data/curated/institution_locations.csv"
INSTITUTIONS = "data/curated/institutions.csv"
PUBLIC_PAPERS = "web/data/public_preview_papers.json"
PUBLIC_MAP = "web/data/public_preview_map_data.json"
FALCON = "curated:c495f498c11dab35ecbc"
WIFS = "curated:2117831292318de4cf18"
FORENSICS_BENCH = "curated:762982679d91cd198a41"
FALCON_MAPPINGS = {
    "mapping:59717de03fbe53a3b5b5": ("institution:6bdc62fb06ac696f", "location:24ff901ade26602be031"),
    "mapping:6456b8bdf7002d769476": ("institution:11d4e5b507bbbada", "location:746e8c5352691ed57b23"),
    "mapping:22611f0898a942d4554e": ("institution:42d2e85e0328361b", "location:31be200653d3e8540ffd"),
    "mapping:049f07debf3a1d281504": ("institution:be8fe6da68f67876", "location:be8fe6da68f67876f00e"),
}
SOURCE_HASHES = {
    PAPERS: "6ac7c17fbdb0a21d4f61c789e5c3973d2ea1c773fa38fb0df9d366bbd6ebee13",
    MAPPINGS: "d9f126b14f0ecae724a2bc91643874aa2b53551f22724509f3589072b3e6b85f",
    DECISIONS: "6fe7b6f5f7d4d0ed1811931fa0c284e9f0b6164c4369023e5f1317bf1626f36e",
}
DECISION_IDS = {
    "U011": "review:410009098fd755a3b7e5",
    "U013": "review:512c3d0bff2f30b88971",
    "U015": "review:86d6197e1a551db7b996",
    "U019": "review:ef5dda51e5ffa783c91d",
    "U020": "review:6ae74616ba17766dfab7",
    "U021": "review:08143b790469625fb4bd",
    "P478": "review:71b971bd40bf491ecbc1",
    "U022": "review:2a957b63e8cb75022e18",
    "L028": "review:be189a1cc5aaa3022219",
}
ACCEPTED = {"U011", "P478", "L028"}
LEGACY_CLOSURES = {"review:b9f458d69de24b8aae0a": "R267", "review:aa32e93a24ade10ed99d": "R236"}


@lru_cache(maxsize=None)
def published(path):
    return subprocess.check_output(
        ["git", "--no-optional-locks", "show", f"{BASELINE}:{path}"], cwd=ROOT
    )


def current(path):
    return (ROOT / path).read_bytes()


def csv_rows(raw):
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline="")))


def by_key(records, field):
    keyed = {row[field]: row for row in records}
    assert len(keyed) == len(records)
    return keyed


def changed_fields(before, after, key):
    old, new = csv_rows(before), csv_rows(after)
    assert [row[key] for row in old] == [row[key] for row in new]
    return {
        a[key]: {field: (a[field], b[field]) for field in a if a[field] != b[field]}
        for a, b in zip(old, new, strict=True) if a != b
    }


def verify_authoritative(read=current):
    assert changed_fields(published(MAPPINGS), read(MAPPINGS), "mapping_id") == {
        mid: {"mapping_status": ("needs_review", "active")} for mid in FALCON_MAPPINGS
    }
    assert changed_fields(published(PAPERS), read(PAPERS), "paper_id") == {
        WIFS: {"venue_track": ("workshops", "Main")}
    }
    for path in [LOCATIONS, INSTITUTIONS, "data/curated/institution_hierarchy.csv", "data/curated/paper_taxonomy.csv"]:
        assert read(path) == published(path)
    raw = read(DECISIONS)
    old = published(DECISIONS)
    assert raw.startswith(old) and len(csv_rows(old)) == 151
    ledger = by_key([row for row in decision_rows(load_queues(ROOT)) if row["batch"] == "B"], "review_id")
    records = csv_rows(raw)
    assert len(records) == len(by_key(records, "decision_id")) == 160
    expected_ids = []
    for rid, record in zip(DECISION_IDS, records[151:], strict=True):
        expected_ids.append(record["decision_id"])
        assert record["review_note"].startswith(f"Batch B review {rid};")
        assert record["action"] == ("no_action_after_review" if rid in ACCEPTED else "unresolved")
        fingerprint = hashlib.sha256(json.dumps(
            {"review_id": rid, "original_question": ledger[rid]},
            sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        ).encode()).hexdigest()
        assert f"[action:{fingerprint}]" in record["review_note"]
        if rid == "P478":
            assert "Special Session – Synthetic Media Detection in Multi-Media Forensics I" in record["review_note"]
    assert expected_ids == list(DECISION_IDS.values())
    assert {p: hashlib.sha256(read(p)).hexdigest() for p in SOURCE_HASHES} == SOURCE_HASHES


def paper_pair_index(papers, markers):
    index = PaperIdentityIndex(papers, PaperIdentityCache())
    def unique_paper(row):
        matches = index.matches(row)
        assert len(matches) == 1
        return index.positions[id(matches[0])]
    pairs = {}
    for marker in markers:
        key = unique_paper(marker), marker["institution_id"]
        assert key not in pairs
        pairs[key] = marker
    return pairs


def verify_public_projection(read=current):
    baseline_papers, papers = [json.loads(load(PUBLIC_PAPERS))["records"] for load in (published, read)]
    baseline_map, map_rows = [json.loads(load(PUBLIC_MAP))["records"] for load in (published, read)]
    old_index = PaperIdentityIndex(baseline_papers, PaperIdentityCache())
    assert len(baseline_papers) == len(papers) == 674
    falcon_pos, wifs_pos, bench_pos = (
        next(i for i, p in enumerate(baseline_papers) if p.get("paper_id") == pid)
        for pid in (FALCON, WIFS, FORENSICS_BENCH)
    )
    assert sum("paper_id" not in row for row in baseline_papers) == 164
    assert len({r["id"] for r in map_rows}) == len(map_rows) == 1414
    for i, (a, b) in enumerate(zip(baseline_papers, papers, strict=True)):
        assert old_index.matches(b) == [a]
        assert ("paper_id" in a, a.get("paper_id")) == ("paper_id" in b, b.get("paper_id"))
        if i not in {falcon_pos, wifs_pos}:
            assert a == b
        for key in ["doi", "arxiv_id", "title", "venue_id", "publication_type", "tasks", "image_scopes", "research_types"]:
            assert a.get(key) == b.get(key)
    old_pairs = paper_pair_index(baseline_papers, baseline_map)
    new_pairs = paper_pair_index(papers, map_rows)
    assert len(old_pairs) == 1410
    assert old_pairs.keys() <= new_pairs.keys()
    assert all(new_pairs[pair] == record for pair, record in old_pairs.items())
    assert new_pairs.keys() - old_pairs.keys() == {(falcon_pos, iid) for iid, _ in FALCON_MAPPINGS.values()}
    assert len({i for i, _ in old_pairs}) == 613 and len({i for i, _ in new_pairs}) == 614
    hku = {iid for i, iid in old_pairs if i == bench_pos}
    assert hku == {iid for i, iid in new_pairs if i == bench_pos}
    assert len(hku) == 8
    assert {"institution:404cfa1ef241f359", "institution:0094b55826d7cf3e"} <= hku
    mappings = by_key(csv_rows(read(MAPPINGS)), "mapping_id")
    locations = by_key(csv_rows(read(LOCATIONS)), "location_id")
    institutions = by_key(csv_rows(read(INSTITUTIONS)), "institution_id")
    for mid, (iid, lid) in FALCON_MAPPINGS.items():
        source = mappings[mid]
        marker = new_pairs[falcon_pos, iid]
        location = locations[lid]
        assert source["paper_id"] == FALCON and source["institution_id"] == iid
        assert institutions[iid]["institution_status"] == "active"
        assert location["coordinate_status"] == "known" and location["institution_id"] == iid
        assert marker["mapping_id"] == mid
        assert marker["id"] == "curated-map:" + hashlib.sha256(mid.encode()).hexdigest()[:20]
        authors = source["institution_authors"].split("; ")
        assert marker["institution_authors"] == authors
        assert marker["current_institution"]["institution_id"] == iid
        assert marker["current_institution"]["index"] == int(source["affiliation_order"])
        assert [a["name"] for a in marker["authors"] if a["is_current_marker_author"]] == authors
        assert all(a["affiliation_source"] == "curated_admin" for a in marker["authors"])
        assert marker["location_id"] == lid
        assert float(marker["lat"]) == float(location["lat"])
        assert float(marker["lon"]) == float(location["lon"])
        assert float(marker["latitude"]) == float(location["lat"])
        assert float(marker["longitude"]) == float(location["lon"])
    before, after = baseline_papers[falcon_pos], papers[falcon_pos]
    assert [a["name"] for a in before["authors"]] == [a["name"] for a in after["authors"]]
    assert [a["affiliation_indices"] for a in after["authors"]] == [[i] for i in (1, 1, 1, 2, 3, 1, 4, 4, 3)]
    assert all(a["affiliation_source"] == "curated_admin" for a in after["authors"])
    assert after["map_record_count"] == 4 and after["has_map_location"]
    before, after = baseline_papers[wifs_pos], papers[wifs_pos]
    assert before["venue_track"] == "Workshop" and after["venue_track"] == "Main"
    assert after["venue_id"] == "venue:wifs" and after["venue_label"] == before["venue_label"]
    assert not after["venue_review_required"] and "venue_review_reason" not in after
    assert {k for k in before.keys() | after.keys() if before.get(k) != after.get(k)} == {
        "venue_track", "venue_review_required", "venue_review_reason", "metadata_status",
    }


def test_authoritative_changes_and_nine_native_decisions():
    verify_authoritative()


def test_exact_public_relationship_set_and_paper_projection():
    verify_public_projection()


def test_current_generated_reports_are_fresh():
    from scripts.audit_key_paper_coverage import validate_artifacts

    assert validate_artifacts(ROOT) == []
    before = csv_rows(published("data/manual/missing_author_mappings_report.csv"))
    after = csv_rows(current("data/manual/missing_author_mappings_report.csv"))
    assert len(before) == len(after) == 674
    changed = [(a, b) for a, b in zip(before, after, strict=True) if a != b]
    assert len(changed) == 1
    old, new = changed[0]
    assert old["paper_id"] == new["paper_id"] == FALCON
    assert {key: (old[key], new[key]) for key in old if old[key] != new[key]} == {
        "current_mapping_state": ("pending", "confirmed"),
        "marker_count": ("0", "4"),
    }


def test_ledger_accounting_from_original_action_inventory():
    ledger = by_key([r for r in decision_rows(load_queues(ROOT)) if r["batch"] == "B"], "review_id")
    taxonomy = csv_rows(current("data/curated/paper_taxonomy.csv"))
    index = PaperIdentityIndex(taxonomy, PaperIdentityCache())
    active_ids = set()
    for paper in json.loads(current(PUBLIC_PAPERS))["records"]:
        matches = index.matches(paper)
        assert len(matches) == 1
        active_ids.add(paper.get("paper_id") or matches[0]["taxonomy_id"])
    closed = set()
    for row in csv_rows(current(DECISIONS)):
        if row["action"] != "no_action_after_review":
            continue
        match = re.search(r"\bBatch B review ([A-Z]\d{3});", row["review_note"])
        rid = match[1] if match else LEGACY_CLOSURES.get(row["decision_id"])
        if rid:
            assert rid in ledger and rid not in closed
            closed.add(rid)
    unresolved = set(ledger) - closed
    assert len(ledger) == 159 and len(unresolved) == 103
    assert sum(ledger[rid]["paper_id"] in active_ids for rid in unresolved) == 101
    assert set(DECISION_IDS) & closed == ACCEPTED


@pytest.mark.parametrize("path,before,after", [
    (MAPPINGS, b"mapping:59717de03fbe53a3b5b5", b"mapping:aaaaaaaaaaaaaaaaaaaa"),
    (MAPPINGS, b"location:24ff901ade26602be031", b"location:aaaaaaaaaaaaaaaaaaaa"),
    (MAPPINGS, b",Changsha University of Science and Technology,", b",Unverified Institution,"),
    (PAPERS, b"curated:2117831292318de4cf18", b"curated:aaaaaaaaaaaaaaaaaaaa"),
    (DECISIONS, b"review:", b"revieW:"),
    (LOCATIONS, b"28.0705674", b"28.0705675"),
])
def test_unauthorized_source_mutation_is_rejected(path, before, after):
    original = current(path)
    assert before in original
    tampered = original.replace(before, after, 1)
    with pytest.raises(AssertionError):
        verify_authoritative(lambda p: tampered if p == path else current(p))


@pytest.mark.parametrize("path,key,field,value", [
    (MAPPINGS, "mapping_id", "affiliation_order", "9"),
    (PAPERS, "paper_id", "venue_track", "Workshop"),
])
def test_unauthorized_curated_field_edit_is_rejected(path, key, field, value):
    records = csv_rows(current(path))
    record_id = next(iter(FALCON_MAPPINGS)) if path == MAPPINGS else WIFS
    by_key(records, key)[record_id][field] = value
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(records[0]))
    writer.writeheader()
    writer.writerows(records)
    raw = stream.getvalue().encode()
    with pytest.raises(AssertionError):
        verify_authoritative(lambda p: raw if p == path else current(p))


@pytest.mark.parametrize("kind", [
    "remove_existing_pair", "change_existing_coordinate", "change_new_coordinate", "duplicate_pair",
    "change_new_marker_mapping", "change_new_marker_authors", "change_new_affiliation_order",
])
def test_unapproved_relationship_changes_are_rejected(kind):
    map_data = json.loads(current(PUBLIC_MAP))
    rows = map_data["records"]
    if kind == "remove_existing_pair":
        rows.pop(0)
    elif kind == "change_existing_coordinate":
        rows[0]["latitude"] += 0.01
    elif kind == "change_new_coordinate":
        next(r for r in rows if r.get("paper_id") == FALCON)["latitude"] += 0.01
    elif kind == "duplicate_pair":
        rows[1] = deepcopy(rows[0])
    elif kind == "change_new_marker_mapping":
        next(r for r in rows if r.get("paper_id") == FALCON)["mapping_id"] = "unverified"
    elif kind == "change_new_marker_authors":
        next(r for r in rows if r.get("paper_id") == FALCON)["institution_authors"] = []
    else:
        papers = json.loads(current(PUBLIC_PAPERS))
        target = next(p for p in papers["records"] if p.get("paper_id") == FALCON)
        target["authors"][0]["affiliation_indices"] = [4]
    def read(path):
        if path == PUBLIC_MAP:
            return json.dumps(map_data).encode()
        if kind == "change_new_affiliation_order" and path == PUBLIC_PAPERS:
            return json.dumps(papers).encode()
        return current(path)
    with pytest.raises(AssertionError):
        verify_public_projection(read)
