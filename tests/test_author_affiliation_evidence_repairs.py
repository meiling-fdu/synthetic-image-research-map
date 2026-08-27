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

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data/curated"
PUBLIC = ROOT / "web/data"


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
    assert list(survey) == ["Thanh Thi Nguyen", "Cuong M. Nguyen", "Dung Tien Nguyen", "Duc Thanh Nguyen", "Saeid Nahavandi"]
    assert all(value == [1] for value in survey.values())


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
                    and mapping["provenance_source"].startswith(("Visually verified paper PDF:", "Verified structured author-affiliation metadata:")))
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


def test_unresolved_roster_remains_visible_and_has_durable_review_notes():
    records = json.loads((PUBLIC / "public_preview_papers.json").read_text())["records"]
    unresolved = {a["name"] for p in records for a in p["authors"] if not a["affiliation_indices"]}
    assert unresolved == {
        "Hainan Ren", "Jia Wang", "Yuexuan Tan", "Jason Li", "Henan Wang",
        "Aruna J. Chamatkar", "Chuah ChaiWen", "Daniel S. Yeung", "Reid Southen", "Usha Kosarkar",
    }
    notes = {r["affected_authors"]: r for r in csv_rows("institution_audit_log.csv")
             if r["action"] == "author_affiliation_unresolved"}
    assert unresolved <= notes.keys()
    assert all(notes[name]["evidence_url"] and notes[name]["review_note"] for name in unresolved)
    assert all(any(a["affiliation_indices"] for a in p["authors"]) for p in records)


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
