"""Paper-specific matrices reviewed on 2026-08-27, not inferred coauthorship."""

import csv
import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.export_public_preview import add_public_detail_fields
from scripts.public_relationships import ReviewedRelationshipResolver
from scripts.author_affiliation_reviews import (
    ACTION, AuthorReviewIndex, annotate_author, affiliation_counts,
    is_non_institutional, review_payload, author_status_errors, review_mapping_conflicts,
)
from scripts.report_missing_author_mappings import author_coverage, build_report_rows
from scripts.validate_public_preview import validate_paper_record

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data/curated"
PUBLIC = ROOT / "web/data"
# These source-roster spellings have no matching active curated author. Old
# automatic markers previously masked the conflict; do not invent a name merge.
# Current public records that still lack a complete curated affiliation roster.
# Hyejoo Choi and Jiarui Wang were resolved by later source-backed imports.
REMAINING_UNRESOLVED_AUTHORS = {"Daniel S. Yeung", "Gopal Sarkarkar", "Shilpa Gedam"}
CURRENT_NON_INSTITUTIONAL_AUTHORS = {
    "Hainan Ren", "Henan Wang", "Reid Southen", "Changtao Miao",
    "Chenzhuo Zhao",
}


def csv_rows(name):
    with (CURATED / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def paper(prefix):
    return next(row for row in json.loads(
        (PUBLIC / "public_preview_papers.json").read_text()
    )["records"] if row["title"].casefold().startswith(prefix.casefold()))


def indices(row):
    return {author["name"]: author["affiliation_indices"] for author in row["authors"]}


def test_synerdetect_exact_author_order_and_superscript_matrix():
    row = paper("SynerDetect:")
    assert list(indices(row)) == [
        "Shuaibo Li", "Yijun Yang", "Zhaohu Xing", "Hongqiu Wang",
        "Pengfei Hao", "Xingyu Li", "Zekai Liu", "Qing Zhang", "Lei Zhu",
    ]
    assert list(indices(row).values()) == [[1]] * 7 + [[3], [1, 2]]
    assert [a["institution_id"] for a in row["affiliations"]] == [
        "institution:942667142da716c5", "institution:fa80d3c071c298e1",
        "institution:5c85faa51cc57a24",
    ]


@pytest.mark.parametrize("prefix,author,expected", [
    ("The Face Deepfake Detection Challenge", "Roberto Caldelli", [7, 8]),
    ("Deepfake Generation and Detection:", "Vrince Vimal", [5, 6]),
    ("Beyond the Spectrum:", "Ning Yu", [2, 3]),
    ("Complement Face Forensic", "Stefanos Zafeiriou", [1, 2]),
    ("Complement Face Forensic", "Kritaphat Songsri-in", [1]),
    ("An Improved Dense CNN", "Pronaya Bhattacharya", [2]),
])
def test_multi_affiliations_and_single_affiliation_boundaries(prefix, author, expected):
    assert indices(paper(prefix))[author] == expected


def test_radar_keeps_the_paper_specific_beijing_location():
    row = paper("RADAR: Reasoning")
    assert indices(row)["Haochen Wang"] == [1]
    assert indices(row)["Xiaolong Jiang"] == [4]
    mapping = next(m for m in csv_rows("author_institution_mappings.csv")
                   if m["title"].startswith("RADAR: Reasoning")
                   and m["institution_authors"] == "Xiaolong Jiang")
    assert mapping["location_id"] == "location:3b46f8ed6f87860347da"


def test_publisher_name_corrections_and_duplicate_consolidation():
    assert "Xiaomeng Fu" in indices(paper("Adaptive Test-Time"))
    assert "Xiaoqin Fu" not in indices(paper("Adaptive Test-Time"))
    assert list(indices(paper("Beyond Known Fakes:")))[0] == "Li Wang"
    attribution = indices(paper("On Attribution of Deepfakes"))
    assert list(attribution) == ["Baiwu Zhang", "Jin Peng Zhou", "Ilia Shumailov", "Nicolas Papernot"]
    assert attribution["Jin Peng Zhou"] == [1, 2]
    assert attribution["Ilia Shumailov"] == [1, 2, 3]
    survey = indices(paper("Deep Learning for Deepfakes Creation"))
    assert list(survey) == ["Thanh Thi Nguyen", "Quoc Viet Hung Nguyen", "Dung Tien Nguyen", "Duc Thanh Nguyen", "Thien Huynh-The", "Saeid Nahavandi", "Thanh Tam Nguyen", "Quoc-Viet Pham", "Cuong M. Nguyen"]
    assert list(survey.values()) == [[1], [2], [1], [1], [3], [1], [4], [5], [6]]


def test_repaired_coordinate_missing_links_survive_repeated_detail_passes():
    row = deepcopy(paper("Deepfake Generation and Detection:"))
    expected = indices(row)
    for _ in range(3):
        add_public_detail_fields([row], [])
        assert indices(row) == expected
        assert all(indices(row).values())


def test_every_new_mapping_has_exact_author_positions_and_unique_order():
    papers = {p["paper_id"]: p for p in csv_rows("papers.csv")}
    institutions = {i["institution_id"]: i for i in csv_rows("institutions.csv")}
    orders = {}
    logical = set()
    for mapping in csv_rows("author_institution_mappings.csv"):
        # Location-only follow-up audits legitimately update timestamps. The
        # original evidence provenance/creation date still identifies the batch.
        if not (mapping["updated_at"] == "2026-08-27T00:30:00Z"
                or (mapping["created_at"] == "2026-08-27T00:30:00Z"
                    and mapping["provenance_source"].startswith(("Visually verified paper PDF:", "Verified structured author-affiliation metadata:", "Visually verified formal publication:")))
                or mapping["provenance_source"].startswith("Visually verified formal publication:")
                or mapping["paper_id"] == "curated:c071c25bc2957d78569b"
                or mapping["mapping_id"] in {"mapping:e52721d76b4e36468169", "mapping:deakin-waurn-ponds-20260827"}):
            continue
        assert mapping["mapping_status"] == "active"
        assert institutions[mapping["institution_id"]]["institution_status"] == "active"
        authors = papers[mapping["paper_id"]]["authors"].split("; ")
        positions = [int(value) for value in mapping["author_order"].split("; ")]
        names = mapping["institution_authors"].split("; ")
        assert [authors[position - 1] for position in positions] == names
        for name in names:
            key = (mapping["paper_id"], name, mapping["institution_id"])
            assert key not in logical
            logical.add(key)
        orders.setdefault(mapping["paper_id"], []).append(int(mapping["affiliation_order"]))
    assert len(logical) > 100
    for values in orders.values():
        assert sorted(values) == list(range(1, len(values) + 1))


def test_unindexed_roster_remains_visible_and_has_durable_review_notes():
    records = json.loads((PUBLIC / "public_preview_papers.json").read_text())["records"]
    unresolved = {a["name"] for p in records for a in p["authors"] if not a["affiliation_indices"]}
    reviewed_unindexed = {
        *CURRENT_NON_INSTITUTIONAL_AUTHORS,
        *REMAINING_UNRESOLVED_AUTHORS,
    }
    legacy_expected = reviewed_unindexed
    assert legacy_expected <= unresolved
    notes = {r["affected_authors"]: r for r in csv_rows("institution_audit_log.csv")
             if r["action"] in {"author_affiliation_unresolved", "author_affiliation_review"}
             and r["affected_authors"] in reviewed_unindexed}
    assert reviewed_unindexed <= notes.keys()
    assert all(notes[name]["evidence_url"] and notes[name]["review_note"] for name in reviewed_unindexed)
    preliminary_authors = {
        name
        for mapping in csv_rows("author_institution_mappings.csv")
        if mapping["mapping_status"] == "needs_review"
        for name in mapping["institution_authors"].split("; ")
        if name
    }
    assert unresolved - legacy_expected <= preliminary_authors
    zero_indexed = [p for p in records if not any(a["affiliation_indices"] for a in p["authors"])]
    assert all(p.get("preliminary_affiliations") for p in zero_indexed)
    assert all(
        {a["name"] for a in p["authors"]} <= preliminary_authors
        for p in zero_indexed
    )


@pytest.mark.parametrize("name", ["Daniel S. Yeung"])
def test_final_unresolved_evidence_pass_preserves_roster_and_does_not_infer_institution(name):
    audit = json.loads((ROOT / "docs/evidence_resolution_2026-08-28.json").read_text())
    case = next(c for c in audit["authors"] if c["author"] == name)
    current = paper(case["title"])
    assert [(a["name"], a["affiliation_indices"]) for a in current["authors"]] == [
        (a["name"], a["affiliation_indices"]) for a in case["before_roster"]
    ]
    author = next(a for a in current["authors"] if a["name"] == name)
    assert author["affiliation_status"] == "unresolved"
    assert not author["affiliation_indices"]
    assert author["affiliation_review"]["review_note"] == case["reason"]
    assert not is_non_institutional(author)


@pytest.mark.parametrize("prefix,name", [
    ("Fake Detection Based", "Jia Wang"),
    ("A Novel Framework", "Aruna J. Chamatkar"),
    ("Deepfake Image Detection Using ResNet50", "Chuah ChaiWen"),
    ("Revealing and Classification", "Usha Kosarkar"),
])
def test_new_publisher_or_paper_evidence_resolves_prior_unindexed_author(prefix, name):
    author = next(a for a in paper(prefix)["authors"] if a["name"] == name)
    assert author["affiliation_status"] == "mapped"
    assert author["affiliation_indices"]


def author_review(status="non_institutional", kind="independent", text="Independent Researcher"):
    return {
        "action": ACTION, "audit_id": "review:1", "paper_id": "paper:review",
        "affected_authors": "Ada Example", "evidence_url": "https://example.org/paper.pdf",
        "review_note": "Reviewed title-page author block", "created_at": "2026-08-27T00:00:00Z",
        "confirmation_text": json.dumps({"status": status, "reason_kind": kind, "source_text": text}),
    }


@pytest.mark.parametrize("kind,text", [
    ("independent", "Independent Researcher"), ("role_only", "Concept Artist"),
    ("contact_only", "Ada Example. e-mail: ada@example.org"),
])
def test_explicit_non_institutional_author_is_complete_without_a_fake_institution(kind, text, monkeypatch):
    review = author_review(kind=kind, text=text)
    monkeypatch.setattr("scripts.export_public_preview.load_author_reviews", lambda: [review])
    monkeypatch.setattr("scripts.report_missing_author_mappings.load_author_reviews", lambda: [review])
    record = {"paper_id": "paper:review", "title": "Example", "year": 2026,
              "authors": [{"name": "Ada Example", "affiliation_indices": []}],
              "missing_affiliation": True, "missing_coordinates": True}
    for _ in range(3):
        add_public_detail_fields([record], [])
        assert record["authors"][0]["name"] == "Ada Example"
        assert record["authors"][0]["affiliation_review"]["source_text"] == text
        assert is_non_institutional(record["authors"][0])
        assert record["affiliations"] == []
        assert record["current_institution"] is None
        assert record["affiliation_complete"]
        assert not record["missing_affiliation"] and not record["missing_coordinates"]
    row, = build_report_rows([record], [], [], [], [])
    assert (row["mapped_authors"], row["non_institutional_authors"], row["missing_authors"]) == (0, 1, 0)
    assert row["mapping_status"] == "complete"
    issues = []
    validate_paper_record(0, record, issues)
    assert not [i for i in issues if i.level == "WARNING"]


@pytest.mark.parametrize("kind,text", [("conflicting_sources", ""), ("geographic_only", "Hong Kong, China")])
def test_conflict_and_geography_only_remain_unresolved(kind, text):
    record = {"paper_id": "paper:review"}
    author = annotate_author(record, {"name": "Ada Example", "affiliation_indices": []},
                             AuthorReviewIndex([author_review("unresolved", kind, text)]))
    assert author["affiliation_status"] == "unresolved"
    assert author_coverage({"authors": [author]}) == (1, 0, ["Ada Example"])


def test_blank_affiliation_does_not_automatically_mean_non_institutional():
    author = annotate_author({}, {"name": "Ada Example", "affiliation_indices": []}, AuthorReviewIndex())
    assert author["affiliation_status"] == "unresolved"
    assert author_status_errors({**author, "affiliation_status": "non_institutional"})
    assert author_status_errors({**author, "affiliation_status": "non_institutional", "affiliation_review": "unverified"})
    with pytest.raises(ValueError, match="supported reason kind"):
        review_payload(author_review(kind="geographic_only", text="Hong Kong, China"))


def test_review_requires_exact_paper_and_author_identity_and_cannot_hide_a_mapping():
    row = author_review()
    index = AuthorReviewIndex([row])
    assert index.get({"paper_id": "paper:other"}, "Ada Example") is None
    assert index.get({"paper_id": "paper:review"}, "A. Example") is None
    with pytest.raises(ValueError, match="has an institution mapping"):
        annotate_author({"paper_id": "paper:review"}, {"name": "Ada Example", "affiliation_indices": [1]}, index)
    assert review_mapping_conflicts([row], [{"paper_id": "paper:review", "mapping_status": "active", "institution_authors": "Ada Example", "mapping_id": "mapping:1"}])


def test_mixed_mapped_and_reviewed_non_institutional_paper_is_complete(monkeypatch):
    monkeypatch.setattr("scripts.report_missing_author_mappings.load_author_reviews", lambda: [author_review()])
    p = {"paper_id": "paper:review", "authors": [
        {"name": "Institution Author", "affiliation_indices": [1]},
        {"name": "Ada Example", "affiliation_indices": []},
    ]}
    row, = build_report_rows([p], [], [], [], [])
    assert (row["mapped_authors"], row["non_institutional_authors"], row["missing_authors"]) == (1, 1, 0)
    assert row["mapping_status"] == "complete"


def test_newer_review_can_reopen_non_institutional_case():
    old = author_review()
    new = {**author_review("unresolved", "conflicting_sources", ""), "created_at": "2026-08-28T00:00:00Z"}
    assert AuthorReviewIndex([new, old]).get({"paper_id": "paper:review"}, "Ada Example")["status"] == "unresolved"


def test_new_supported_mapping_can_supersede_an_unresolved_review():
    old = author_review("unresolved", "conflicting_sources", "")
    new = {**author_review("mapped"), "created_at": "2026-08-28T00:00:00Z"}
    author = annotate_author({"paper_id": "paper:review"}, {"name": "Ada Example", "affiliation_indices": [1]}, AuthorReviewIndex([old, new]))
    assert author["affiliation_status"] == "mapped"
    assert not review_mapping_conflicts([old, new], [{"paper_id": "paper:review", "mapping_status": "active", "institution_authors": "Ada Example"}])


def test_final_repository_author_states_follow_formal_rosters():
    records = json.loads((PUBLIC / "public_preview_papers.json").read_text())["records"]
    noninstitutional = {a["name"] for p in records for a in p["authors"] if is_non_institutional(a)}
    assert noninstitutional == CURRENT_NON_INSTITUTIONAL_AUTHORS
    unresolved = {a["name"] for p in records for a in p["authors"] if a["affiliation_status"] == "unresolved"}
    legacy_expected = REMAINING_UNRESOLVED_AUTHORS
    assert legacy_expected <= unresolved
    preliminary_authors = {
        name
        for mapping in csv_rows("author_institution_mappings.csv")
        if mapping["mapping_status"] == "needs_review"
        for name in mapping["institution_authors"].split("; ")
        if name
    }
    assert unresolved - legacy_expected <= preliminary_authors
    assert sum(p["affiliation_complete"] for p in records) == sum(
        not any(a["affiliation_status"] == "unresolved" for a in p["authors"])
        for p in records
    )
    for p in records:
        assert p["author_affiliation_counts"] == affiliation_counts(p["authors"])
    entities = {r["canonical_name"] for r in csv_rows("institutions.csv")}
    assert not entities & {"Independent Researcher", "Concept Artist", "Freelancer", "Independent"}


@pytest.mark.parametrize("doi,confirmation,removed", [
    ("10.1000/one", "paper_doi=10.1000/one", True),
    ("10.1000/two", "paper_doi=10.1000/one", False),
    ("10.1000/one", "", False),
])
def test_automatic_removal_requires_exact_doi(doi, confirmation, removed):
    marker = {"doi": doi, "institution_id": "institution:one", "institution_authors": ["Ada Example"]}
    audit = {"action": "mapping_removed", "paper_id": "paper:one",
             "previous_institution_id": "institution:one", "previous_authors": "Ada Example",
             "confirmation_text": confirmation}
    kept, count = ReviewedRelationshipResolver([], [audit]).filter_superseded([marker])
    assert count == int(removed)
    assert kept == ([] if removed else [marker])


def test_export_preserves_authoritative_admin_rows(tmp_path):
    locations = {r["institution_id"]: r for r in csv_rows("institution_locations.csv")}
    assert (locations["institution:c45f90fe3d40e0f7"]["lat"],
            locations["institution:c45f90fe3d40e0f7"]["lon"]) == ("43.318744", "124.334624")
    assert (locations["institution:0be9d444a6c88894"]["lat"],
            locations["institution:0be9d444a6c88894"]["lon"]) == ("39.9458", "116.4217")
    mapping = next(r for r in csv_rows("author_institution_mappings.csv")
                   if r["mapping_id"] == "mapping:457e9e85050e4ece4e76")
    assert mapping["institution_id"] == "institution:a1ff6f7123083db9"
    assert mapping["institution_authors"] == "Jian Zhao"
    assert mapping["affiliation_order"] == "3"
    before = {p: p.read_bytes() for p in CURATED.glob("*.csv")}
    for filename in ("public_preview_map_data.json", "public_preview_papers.json"):
        shutil.copyfile(PUBLIC / filename, tmp_path / filename)
    shutil.copyfile(CURATED / "institution_location_review.csv", tmp_path / "review.csv")
    result = subprocess.run([
        sys.executable, "scripts/export_public_preview.py", "--preserve-existing",
        "--output", str(tmp_path / "public_preview_map_data.json"),
        "--paper-output", str(tmp_path / "public_preview_papers.json"),
        "--location-review", str(tmp_path / "review.csv"),
    ], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert all(p.read_bytes() == content for p, content in before.items())
    exported = json.loads((tmp_path / "public_preview_papers.json").read_text())["records"]
    forgery = next(p for p in exported if p["title"].startswith("ForgeryMoE"))
    assert indices(forgery)["Jian Zhao"] == [3]
