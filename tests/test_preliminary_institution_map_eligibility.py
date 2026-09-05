import subprocess
from copy import deepcopy
from pathlib import Path

from scripts.curated_export import (
    build_curated_map_records,
    integrate_curated_records,
)
from scripts.export_public_preview import (
    add_public_detail_fields,
    apply_ordered_paper_location_summaries,
)


ROOT = Path(__file__).resolve().parents[1]
NODE = Path(
    "/Users/meilinger/.cache/codex-runtimes/codex-primary-runtime/"
    "dependencies/node/bin/node"
)


def fixture():
    paper = {
        "paper_id": "curated:pending",
        "title": "Pending paper with sourced affiliation",
        "year": 2026,
        "publication_year": 2026,
        "tasks": ["detection"], "image_scopes": ["fully_generated"], "research_types": ["method"],
        "authors": ["Ada Example"],
        "curation_status": "needs_review",
        "review_status": "pending",
    }
    mapping = {
        "mapping_id": "mapping:pending",
        "paper_id": paper["paper_id"],
        "title": paper["title"],
        "year": "2026",
        "institution": "Example University",
        "institution_id": "institution:example",
        "institution_authors": "Ada Example",
        "raw_affiliation": "Department of Examples, Example University",
        "provenance_source": "paper PDF",
        "mapping_status": "needs_review",
    }
    institution = {
        "institution_id": "institution:example",
        "canonical_name": "Example University",
        "institution_status": "active",
    }
    location = {
        "location_id": "location:example",
        "institution_id": "institution:example",
        "institution": "Example University",
        "city": "Rome",
        "country": "Italy",
        "country_code": "IT",
        "lat": "41.9028",
        "lon": "12.4964",
        "coordinate_status": "known",
    }
    return paper, mapping, institution, location


def build(paper, mapping, institution, locations):
    return build_curated_map_records(
        [paper],
        [mapping],
        [],
        confirmed_location_records=locations,
        institution_records=[institution],
    )


def test_needs_review_supported_confirmed_institution_and_location_emits_marker():
    paper, mapping, institution, location = fixture()
    markers, summary = build(paper, mapping, institution, [location])
    assert len(markers) == 1
    assert markers[0]["mapping_id"] == mapping["mapping_id"]
    assert markers[0]["mapping_status"] == "needs_review"
    assert markers[0]["institution_identity_status"] == "confirmed"
    assert markers[0]["institution_location_status"] == "confirmed"
    assert summary["preliminary_markers_created"] == 1


def test_confirmed_institution_with_unresolved_location_emits_no_marker():
    paper, mapping, institution, _location = fixture()
    markers, summary = build(paper, mapping, institution, [])
    assert markers == []
    assert summary["curated_mappings_unresolved_location_excluded"] == 1


def test_unresolved_institution_identity_emits_no_marker():
    paper, mapping, institution, location = fixture()
    institution["institution_status"] = "alias"
    markers, summary = build(paper, mapping, institution, [location])
    assert markers == []
    assert summary["curated_mappings_unresolved_identity_excluded"] == 1


def test_preliminary_affiliation_remains_visible_without_marker():
    paper, mapping, institution, _location = fixture()
    papers, markers, _reviews, _summary = integrate_curated_records(
        [], [], [paper], [mapping], institution_records=[institution]
    )
    add_public_detail_fields(papers, markers)
    assert markers == []
    assert papers[0]["review_status"] == "pending"
    assert papers[0]["map_record_count"] == 0
    assert papers[0]["affiliations"][0]["institution_id"] == "institution:example"
    assert papers[0]["affiliations"][0]["preliminary"] is True


def test_confirming_location_adds_marker_without_changing_paper_review():
    paper, mapping, institution, location = fixture()
    original_review = (paper["curation_status"], paper["review_status"])
    before, _summary = build(paper, mapping, institution, [])
    after, _summary = build(paper, mapping, institution, [location])
    assert before == []
    assert len(after) == 1
    assert (paper["curation_status"], paper["review_status"]) == original_review


def test_existing_confirmed_paper_marker_behavior_is_unchanged():
    paper, mapping, institution, location = fixture()
    paper.update(curation_status="confirmed", review_status="reviewed")
    mapping["mapping_status"] = "active"
    marker_before, _ = build_curated_map_records(
        [deepcopy(paper)], [mapping], [], confirmed_location_records=[location]
    )
    marker_after, _ = build(
        deepcopy(paper), mapping, institution, [location]
    )
    assert len(marker_before) == len(marker_after) == 1
    for field in ("mapping_id", "institution_id", "latitude", "longitude"):
        assert marker_before[0][field] == marker_after[0][field]


def test_mapping_coordinates_are_not_used_without_confirmed_location():
    paper, mapping, institution, _location = fixture()
    mapping.update(institution_latitude="41.9", institution_longitude="12.5")
    markers, _summary = build(paper, mapping, institution, [])
    assert markers == []


def test_numeric_location_without_explicit_confirmation_is_not_used():
    paper, mapping, institution, location = fixture()
    location["coordinate_status"] = ""
    markers, summary = build(paper, mapping, institution, [location])
    assert markers == []
    assert summary["curated_mappings_unresolved_location_excluded"] == 1


def test_export_and_frontend_counts_follow_deduplicated_map_records():
    paper, mapping, institution, location = fixture()
    second_paper = {**paper, "paper_id": "curated:pending-2", "title": "Second"}
    second_mapping = {
        **mapping,
        "mapping_id": "mapping:pending-2",
        "paper_id": second_paper["paper_id"],
        "title": second_paper["title"],
    }
    papers, markers, _reviews, summary = integrate_curated_records(
        [], [], [paper, second_paper], [mapping, second_mapping],
        confirmed_location_records=[location], institution_records=[institution],
    )
    add_public_detail_fields(papers, markers)
    apply_ordered_paper_location_summaries(papers, markers)
    assert len(markers) == summary["preliminary_markers_created"] == 2
    assert all(item["map_record_count"] == 1 for item in papers)

    script = """
const helpers = require(process.argv[1]);
const records = JSON.parse(process.argv[2]);
const groups = helpers.groupInstitutionRecords(
  records, record => record.institution_id, record => record.paper_id
);
if (groups.length !== 1 || groups[0].paperCount !== 2) process.exit(1);
"""
    subprocess.run(
        [str(NODE), "-e", script, str(ROOT / "web/marker_size_helpers.js"),
         __import__("json").dumps(markers)],
        check=True,
    )


def test_active_and_eligible_preliminary_mappings_coexist_and_deduplicate():
    paper, preliminary, institution, preliminary_location = fixture()
    active = {
        **preliminary,
        "mapping_id": "mapping:active",
        "institution": "Confirmed University",
        "institution_id": "institution:confirmed",
        "mapping_status": "active",
    }
    active_institution = {
        "institution_id": "institution:confirmed",
        "canonical_name": "Confirmed University",
        "institution_status": "active",
    }
    active_location = {
        **preliminary_location,
        "location_id": "location:confirmed",
        "institution_id": "institution:confirmed",
        "institution": "Confirmed University",
        "lat": "45.0",
        "lon": "9.0",
    }
    duplicate_preliminary = {
        **preliminary,
        "mapping_id": "mapping:pending-duplicate",
        "institution_authors": "Ben Example",
    }

    papers, markers, _reviews, summary = integrate_curated_records(
        [],
        [],
        [paper],
        [active, preliminary, duplicate_preliminary],
        confirmed_location_records=[active_location, preliminary_location],
        institution_records=[active_institution, institution],
    )

    assert {marker["institution_id"] for marker in markers} == {
        "institution:confirmed",
        "institution:example",
    }
    assert len(markers) == 2
    assert summary["preliminary_markers_created"] == 1
    assert papers[0]["map_record_count"] == 2
    assert papers[0]["curation_status"] == "needs_review"
    assert papers[0]["review_status"] == "pending"
