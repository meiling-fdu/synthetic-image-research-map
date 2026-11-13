"""Verify the published B5-05 ledger and its public-data boundary."""

import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
import re
import subprocess

import pytest

from scripts.audit_key_paper_coverage import validate_artifacts
from scripts.export_public_preview import apply_mapping_exclusion_decisions
from scripts.review_decisions import upsert_review_decision
from scripts.validate_corpus_quality_audit import decision_rows, load_context, load_queues

ROOT = Path(__file__).resolve().parents[1]
PARENT = "9ca5c1c617ba34f24cf2e159f7a94255fddd526a"
LEDGER = "data/curated/review_decisions.csv"
LEDGER_SHA256 = "c59d9fe6113ab33553e8423cde710d9230d82487bebf3d84e34fc3c4e0b938c9"
PARENT_LEDGER_SHA256 = "6fe7b6f5f7d4d0ed1811931fa0c284e9f0b6164c4369023e5f1317bf1626f36e"
HANDOFF_SHA256 = "b33b8af43146533c191d22364875ab9379a18fbbb9390a1608f5957e4490d7ca"
MAP = "web/data/public_preview_map_data.json"
PAPERS = "web/data/public_preview_papers.json"
ACCEPTED = {"L004", "L006", "L008", "L009", "L010", "L011", "L012", "L014"}
HELD = {"L003", "L005", "L007"}
ACTIONS = (
    ("L003", "review:7c78b06750205be02611"),
    ("L004", "review:ab4fc1be102e0f7fac73"),
    ("L005", "review:198ec420c1c7a845a613"),
    ("L006", "review:6b87073c323b6a55b2b8"),
    ("L007", "review:ea312fa2f1ebceec5569"),
    ("L008", "review:5d97db0ac8d8788a15ff"),
    ("L009", "review:bc90e49ae046ed2eed1b"),
    ("L010", "review:cc86e9e43ad8f7d88123"),
    ("L011", "review:c98463fc765d7b01948a"),
    ("L012", "review:bbd1466031261364b45e"),
    ("L014", "review:6ab36fc2ae192265889d"),
)
LEGACY_CLOSURES = {
    "review:b9f458d69de24b8aae0a": "R267",
    "review:aa32e93a24ade10ed99d": "R236",
}


def published(path):
    return subprocess.check_output(
        ["git", "--no-optional-locks", "show", f"{PARENT}:{path}"], cwd=ROOT
    )


def current(path):
    return (ROOT / path).read_bytes()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def rows(raw):
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline="")))


def action_id(row):
    match = re.search(r"\bBatch B review ([A-Z]\d{3});", row["review_note"])
    return match[1] if match else LEGACY_CLOSURES.get(row["decision_id"])


def verify_ledger(previous, candidate):
    assert digest(previous) == PARENT_LEDGER_SHA256, "Immutable B5-04 ledger changed"
    assert candidate.startswith(previous), "Prior decision bytes changed"
    old = rows(previous)
    new = rows(candidate)
    assert len(old) == 160
    assert len(new) == len({r["decision_id"] for r in new}) == 171
    suffix = new[len(old):]
    assert tuple((action_id(r), r["decision_id"]) for r in suffix) == ACTIONS
    assert digest(candidate) == LEDGER_SHA256, "Reviewed B5-05 bytes changed"
    return old, new, suffix


def test_exact_ledger_and_native_action_bindings():
    old, new, suffix = verify_ledger(published(LEDGER), current(LEDGER))
    inventory = {
        row["review_id"]: row for row in decision_rows(load_queues(ROOT)) if row["batch"] == "B"
    }
    context = load_context(ROOT)
    for row in suffix:
        rid = action_id(row)
        question = inventory[rid]
        paper = context["papers"][question["paper_id"]]
        payload = json.dumps(
            {"review_id": rid, "original_question": question},
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        assert f"[action:{digest(payload.encode())}]" in row["review_note"]
        assert question["paper_id"] in row["review_note"]
        assert row["title"] == paper["title"]
        assert row["year"] == str(paper["year"])
        assert row["doi"].casefold() == (paper.get("doi") or "").casefold()
        assert row["review_queue"] == "institution_consistency"
        assert row["target_type"] == "paper"
        assert row["institution"] == ""
        assert HANDOFF_SHA256 in row["review_note"]
        assert f"per_paper/{rid}.json SHA-256" in row["review_note"]
        assert row["action"] == ("no_action_after_review" if rid in ACCEPTED else "unresolved")

    def unresolved(records):
        closed = [
            action_id(row) for row in records
            if row["action"] == "no_action_after_review" and action_id(row)
        ]
        assert len(set(closed)) == len(closed) and set(closed) <= inventory.keys()
        historical = set(inventory) - set(closed)
        active = {
            rid for rid in historical if inventory[rid]["paper_id"] in context["papers"]
        }
        return historical, active

    before_history, before_public = unresolved(old)
    after_history, after_public = unresolved(new)
    assert (len(before_history), len(before_public)) == (103, 101)
    assert (len(after_history), len(after_public)) == (95, 93)
    assert before_history - after_history == before_public - after_public == ACCEPTED
    assert HELD <= after_history & after_public


def test_evidence_caveats_and_exact_wuhan_mapping():
    _, _, suffix = verify_ledger(published(LEDGER), current(LEDGER))
    notes = {action_id(r): r["review_note"] for r in suffix}
    assert all(term in notes["L008"] for term in (
        "Publisher page 1847", "full ACL PDF remained incomplete", "618274 bytes missing",
        "qc/L008_partial_pdf_evidence_assessment.json",
    ))
    assert all(term in notes["L012"] for term in (
        "supersedes the transposed institution-ID comparison", "Run Wang position 6",
        "source marker 5", "qc/L012_additive_correction.json",
        "mapping:2294c4cd637a66a3f33b",
    ))
    mapping, = [
        r for r in rows(current("data/curated/author_institution_mappings.csv"))
        if r["mapping_id"] == "mapping:2294c4cd637a66a3f33b"
    ]
    assert mapping["institution_id"] == "institution:f23b95ce92de4591"
    assert mapping["institution"] == "Wuhan University"
    assert mapping["institution_authors"] == "Run Wang"
    assert mapping["mapping_status"] == "active"


def test_native_idempotence_on_all_eleven_rows(tmp_path):
    _, _, suffix = verify_ledger(published(LEDGER), current(LEDGER))
    candidate = tmp_path / "review_decisions.csv"
    candidate.write_bytes(current(LEDGER))
    state = candidate.read_bytes(), candidate.stat().st_mtime_ns
    for row in suffix:
        assert upsert_review_decision(row, path=candidate) == row
    assert (candidate.read_bytes(), candidate.stat().st_mtime_ns) == state


@pytest.mark.parametrize("path", [
    "data/curated/author_institution_mappings.csv",
    "data/curated/papers.csv",
    "data/curated/paper_taxonomy.csv",
    "data/curated/institutions.csv",
    "data/curated/institution_locations.csv",
    "data/curated/institution_aliases.csv",
    "data/curated/institution_hierarchy.csv",
    "data/curated/institution_audit_log.csv",
    "data/curated/venue_aliases.csv",
    "data/curated/publication_overrides.csv",
    "data/curated/institution_author_overrides.csv",
    PAPERS, MAP,
    "docs/public_preview_report.md",
    "docs/missing_author_mappings_report.md",
    "data/manual/missing_author_mappings_report.csv",
    "docs/key_paper_coverage_report.md",
    "data/manual/key_paper_coverage_report.csv",
])
def test_exact_preservation_of_authoritative_and_generated_paths(path):
    assert current(path) == published(path)


def test_public_relationship_and_paper_projection():
    context = load_context(ROOT)
    assert context["counts"] == {
        "public": 674, "formal": 557, "mapped": 614, "unmapped": 60,
        "relationship_rows": 1414, "unique_paper_institution_pairs": 1414,
    }
    papers = context["papers"].values()
    assert Counter(t for p in papers for t in p["tasks"]) == {
        "detection": 621, "source_attribution": 84, "localization": 45,
    }
    assert Counter(t for p in papers for t in p["research_types"]) == {
        "method": 578, "dataset": 146, "benchmark": 102, "survey": 21, "analysis_study": 90,
    }
    old, new, _ = verify_ledger(published(LEDGER), current(LEDGER))
    markers = json.loads(current(MAP))["records"]
    assert len({row["id"] for row in markers}) == 1414
    assert apply_mapping_exclusion_decisions(markers, old) == apply_mapping_exclusion_decisions(markers, new)
    assert validate_artifacts(ROOT) == []


@pytest.mark.parametrize("kind", ["prefix", "missing", "duplicate", "promoted_hold", "wrong_evidence"])
def test_unapproved_ledger_content_is_rejected(kind):
    prior, live = published(LEDGER), current(LEDGER)
    verify_ledger(prior, live)
    suffix = live[len(prior):]
    match kind:
        case "prefix":
            mutated = live.replace(b"review:", b"revieW:", 1)
        case "missing":
            mutated = prior
        case "duplicate":
            mutated = live + suffix
        case "promoted_hold":
            mutated = prior + suffix.replace(b",unresolved,", b",no_action_after_review,", 1)
        case "wrong_evidence":
            mutated = prior + suffix.replace(HANDOFF_SHA256.encode(), b"0" * 64, 1)
    assert mutated != live
    with pytest.raises(AssertionError):
        verify_ledger(prior, mutated)
