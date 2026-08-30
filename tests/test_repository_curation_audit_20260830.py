"""Regressions for the 2026-08-30 repository-wide curation audit."""

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "curated"
PUBLIC = ROOT / "web" / "data"


def rows(name):
    with (CURATED / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def public_records(name):
    return json.loads((PUBLIC / name).read_text(encoding="utf-8"))["records"]


def test_mlep_final_proceedings_metadata_and_roster_reach_public_output():
    paper = next(row for row in rows("papers.csv") if row["paper_id"] == "curated:828a87e68db4c3541e80")
    expected_authors = "Lin Yuan; Xiaowan Li; Yan Zhang; Jiawei Zhang; Hongbo Li; Xinbo Gao"
    assert paper["authors"] == expected_authors
    assert paper["doi"] == "10.52202/085713-2321"
    assert paper["arxiv_id"] == "2504.13726"
    assert paper["paper_url"].startswith("https://proceedings.neurips.cc/")

    public = next(
        row
        for row in public_records("public_preview_papers.json")
        if row.get("paper_id") == paper["paper_id"]
    )
    assert [author["name"] for author in public["authors"]] == expected_authors.split("; ")
    assert public["doi"] == paper["doi"]
    assert public["arxiv_id"] == paper["arxiv_id"]


def test_realign_preserves_exact_paper_affiliation_membership():
    paper_id = "curated:ce36039d47fbcb9e4e7b"
    mappings = {
        row["affiliation_order"]: row
        for row in rows("author_institution_mappings.csv")
        if row["paper_id"] == paper_id and row["mapping_status"] == "active"
    }
    assert mappings["1"]["institution_authors"] == "Qing Huang; Zhipei Xu; Xuanyu Zhang; Jian Zhang"
    assert mappings["1"]["author_order"] == "1; 2; 3; 5"
    assert mappings["1"]["institution"] == "Peking University"
    assert mappings["1"]["institution_id"] == "institution:46e4866d3b2954ab"
    assert mappings["1"]["location_id"] == "location:46e4866d3b2954ab314b"
    assert mappings["2"]["institution_authors"] == "Qing Huang"
    assert mappings["2"]["institution"] == "South China University of Technology"
    assert mappings["3"]["institution_authors"] == "Xiangyu Yu"
    assert mappings["3"]["institution"] == "South China University of Technology"
    assert mappings["4"]["institution_authors"] == "Jian Zhang"
    assert mappings["4"]["institution"] == "Peking University Shenzhen Graduate School"
    assert mappings["4"]["institution_id"] == "institution:6346b1a9c3b5ccd7"
    assert mappings["4"]["location_id"] == "location:6346b1a9c3b5ccd791ab"

    public = next(row for row in public_records("public_preview_papers.json") if row.get("paper_id") == paper_id)
    affiliations = {row["index"]: row["institution"] for row in public["author_institution_affiliations"]}
    authors = {row["name"]: row["affiliation_indices"] for row in public["authors"]}
    pku_index = next(index for index, name in affiliations.items() if name == "Peking University")
    scut_index = next(index for index, name in affiliations.items() if name == "South China University of Technology")
    pku_shenzhen_index = next(index for index, name in affiliations.items() if name == "Peking University Shenzhen Graduate School")
    assert authors == {
        "Qing Huang": [pku_index, scut_index],
        "Zhipei Xu": [pku_index],
        "Xuanyu Zhang": [pku_index],
        "Xiangyu Yu": [scut_index],
        "Jian Zhang": [pku_index, pku_shenzhen_index],
    }

    markers = [row for row in public_records("public_preview_map_data.json") if row.get("paper_id") == paper_id]
    by_institution = {row["institution"]: row for row in markers}
    assert set(by_institution) == {
        "Peking University",
        "South China University of Technology",
        "Peking University Shenzhen Graduate School",
    }
    assert by_institution["Peking University"]["institution_authors"] == [
        "Qing Huang", "Zhipei Xu", "Xuanyu Zhang", "Jian Zhang"
    ]
    assert by_institution["Peking University Shenzhen Graduate School"]["institution_authors"] == ["Jian Zhang"]
    assert by_institution["Peking University"]["location_id"] == "location:46e4866d3b2954ab314b"
    assert by_institution["Peking University Shenzhen Graduate School"]["location_id"] == "location:6346b1a9c3b5ccd791ab"


def test_generic_peking_affiliation_cannot_resolve_to_pku_shenzhen():
    from scripts.curated_institutions import exact_institution_matches

    institutions = rows("institutions.csv")
    aliases = rows("institution_aliases.csv")
    raw = "School of Electronic and Computer Engineering, Peking University"
    assert exact_institution_matches(raw, institutions, aliases) == ["institution:46e4866d3b2954ab"]

    wrongly_absorbed = [
        row for row in rows("author_institution_mappings.csv")
        if row["institution_id"] == "institution:6346b1a9c3b5ccd7"
        and "peking university" in row["raw_affiliation"].casefold()
        and "shenzhen" not in row["raw_affiliation"].casefold()
    ]
    assert wrongly_absorbed == []


def test_bsi_identity_and_manually_confirmed_location_are_published():
    institution_id = "institution:9a7735d85c857b40"
    institution = next(row for row in rows("institutions.csv") if row["institution_id"] == institution_id)
    assert institution["canonical_name"] == "Federal Office for Information Security"
    assert institution["abbreviation"] == "BSI"
    assert institution["institution_status"] == "active"

    alias = next(row for row in rows("institution_aliases.csv") if row["alias_name"] == "BSI")
    assert alias["institution_id"] == institution_id
    assert alias["review_status"] == "confirmed"

    mapping = next(row for row in rows("author_institution_mappings.csv") if row["mapping_id"] == "mapping:8d3fa7d98587fd34883d")
    assert mapping["institution"] == institution["canonical_name"]
    assert mapping["raw_affiliation"] == "BSI, Saarbrücken, Germany"
    assert mapping["mapping_status"] == "active"
    assert not mapping["location_id"]

    review = next(row for row in rows("institution_location_review.csv") if row["institution_id"] == institution_id)
    assert review["review_status"] == "confirmed"
    assert review["location_status"] == "known"
    assert review["coordinate_status"] == "known"
    assert any(row.get("institution_id") == institution_id for row in public_records("public_preview_map_data.json"))


def test_public_map_has_no_inactive_or_unconfirmed_location_relationships():
    active_ids = {
        row["institution_id"]
        for row in rows("institutions.csv")
        if row["institution_status"] == "active"
    }
    confirmed_locations = {
        row["location_id"]
        for row in rows("institution_locations.csv")
        if row["coordinate_status"] == "known"
    }
    mapping_statuses = {
        row["mapping_id"]: row["mapping_status"]
        for row in rows("author_institution_mappings.csv")
        if row["mapping_status"] in {"active", "needs_review"}
    }
    markers = public_records("public_preview_map_data.json")
    curated_markers = [row for row in markers if row.get("mapping_id")]
    assert curated_markers
    assert all(row["mapping_id"] in mapping_statuses for row in curated_markers)
    assert all(row["institution_id"] in active_ids for row in curated_markers)
    assert all(row["location_id"] in confirmed_locations for row in curated_markers)
    assert all(
        bool(row.get("preliminary_affiliations")) ==
        (mapping_statuses[row["mapping_id"]] == "needs_review")
        for row in curated_markers
    )
    assert all(
        row.get("institution_identity_status") in (None, "confirmed")
        for row in curated_markers
    )
    assert all(
        row.get("institution_location_status") in (None, "confirmed")
        for row in curated_markers
    )
