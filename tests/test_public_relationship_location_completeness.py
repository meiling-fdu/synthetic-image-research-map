from copy import deepcopy

import pytest

from scripts.report_public_relationship_location_completeness import build_report, repository_report, valid_coordinates
from scripts.public_relationships import ReviewedRelationshipResolver


def fixture():
    paper = {"paper_id": "paper:1", "title": "Example", "year": "2025"}
    institution = {"institution_id": "institution:1", "canonical_name": "Example University", "institution_status": "active"}
    mapping = {**paper, "mapping_id": "mapping:1", "institution_id": "institution:1", "institution": "Example University", "mapping_status": "active", "institution_authors": "Ada Example", "location_id": "location:paper"}
    location = {"institution_id": "institution:1", "institution": "Example University", "location_id": "location:paper", "city": "Paper campus", "country": "Italy", "region": "Lazio", "lat": "41.9", "lon": "12.5", "coordinate_status": "known"}
    marker = {**mapping, **location}
    return [[paper], [marker], [mapping], [institution], [location], [], []]


def test_supported_selected_location_is_complete_and_report_is_read_only():
    inputs = fixture()
    before = deepcopy(inputs)
    report = build_report(*inputs)
    assert report[0]["classification"] == "COMPLETE"
    assert report[0]["location_id"] == "location:paper"
    assert inputs == before


def test_another_campus_cannot_hide_missing_paper_location():
    inputs = fixture()
    inputs[1] = []
    inputs[4][0]["location_id"] = "location:headquarters"
    assert build_report(*inputs)[0]["classification"] == "ERROR"


def test_numeric_zero_coordinates_are_preserved_in_report():
    inputs = fixture()
    for row in (inputs[1][0], inputs[4][0]):
        row.update(lat=0, lon=0)
    row, = build_report(*inputs)
    assert row["classification"] == "COMPLETE"
    assert row["latitude"] == row["longitude"] == "0"


def test_unsupported_manual_coordinate_removed_returns_actionable():
    inputs = fixture()
    inputs[1] = []
    inputs[4] = []
    inputs[5] = [{"institution_id": "institution:1", "related_paper_id": "paper:1", "review_status": "pending_review", "coordinate_status": "needs_coordinate_review", "suggested_city": "Paper campus", "suggested_country": "Italy", "evidence_source": "Rejected city centroid; exact campus building is not verified."}]
    report = build_report(*inputs)
    assert report[0]["classification"] == "ACTIONABLE"
    assert report[0]["city"] == "Paper campus"
    assert not report[0]["latitude"] and not report[0]["longitude"]
    inputs[5][0]["evidence_source"] = ""
    assert build_report(*inputs)[0]["classification"] == "ERROR"


def test_stale_export_cannot_outvote_authoritative_location():
    inputs = fixture()
    inputs[1][0]["lat"] = "0"
    assert build_report(*inputs)[0]["classification"] == "ERROR"


def test_confirmed_alias_keeps_site_ownership_and_mapping_lineage():
    inputs = fixture()
    inputs[3].append({"institution_id": "institution:parent", "canonical_name": "Example Parent", "institution_status": "active"})
    inputs[1][0]["institution_id"] = "institution:parent"
    assert build_report(*inputs, redirects={"institution:1": "institution:parent"})[0]["classification"] == "COMPLETE"
    assert build_report(*inputs)[0]["classification"] == "ERROR"


@pytest.mark.parametrize("lat,lon", [("nan", "1"), ("inf", "1"), ("91", "1"), ("1", "181"), ("", "1")])
def test_malformed_coordinates_are_not_usable(lat, lon):
    assert not valid_coordinates({"lat": lat, "lon": lon})


def test_non_active_identity_candidates_are_explicit_not_new_coordinate_queue():
    inputs = fixture()
    inputs[1] = []
    inputs[2][0]["mapping_status"] = "needs_review"
    row, = build_report(*inputs)
    assert row["classification"] == "EXCLUDED"
    assert row["support_source"] == "mapping_not_active"


def test_current_repository_has_zero_silent_geographic_relationships():
    report = repository_report()
    assert not [r for r in report if r["classification"] == "ERROR"]
    actionable = [r for r in report if r["classification"] == "ACTIONABLE"]
    assert len(actionable) == 8
    assert all(r["reason"] and not r["latitude"] and not r["longitude"] for r in actionable)


@pytest.mark.parametrize("changed", [None, "id", "doi", "institution_id", "institution_authors"])
def test_reviewed_initials_and_campus_transition_requires_exact_evidence(changed):
    old = {"id": "legacy:1", "doi": "10.1/paper", "institution_id": "institution:1", "institution_authors": ["A. Example"]}
    target = {"mapping_id": "mapping:1", "mapping_status": "active", "paper_id": "paper:1", "doi": "10.1/paper", "institution_id": "institution:1", "location_id": "location:campus", "institution_authors": "Ada Example"}
    audit = {"action": "mapping_change_confirmed", "paper_id": "paper:1", "previous_institution_id": "institution:1", "institution_id": "institution:1", "mapping_id": "mapping:1", "location_id": "location:campus", "previous_authors": "A. Example", "new_authors": "Ada Example", "confirmation_text": "previous_record_id=legacy:1; paper_doi=10.1/paper"}
    if changed:
        old[changed] = "different"
    resolver = ReviewedRelationshipResolver([target], [audit])
    assert resolver.supersedes(old) is (changed is None)
    assert resolver.superseding_mapping_ids(old) == (("mapping:1",) if changed is None else ())


def test_reviewed_transition_cannot_remove_old_marker_without_current_target():
    old = {"id": "legacy:1", "doi": "10.1/paper", "institution_id": "institution:1", "institution_authors": ["A. Example"]}
    audit = {"action": "mapping_change_confirmed", "paper_id": "paper:1", "previous_institution_id": "institution:1", "institution_id": "institution:1", "mapping_id": "mapping:missing", "location_id": "location:campus", "previous_authors": "A. Example", "new_authors": "Ada Example", "confirmation_text": "previous_record_id=legacy:1; paper_doi=10.1/paper"}
    assert not ReviewedRelationshipResolver([], [audit]).supersedes(old)


@pytest.mark.parametrize('status', ['needs_coordinate_review', 'pending_review', 'ambiguous', 'ignore', 'ignored', 'excluded'])
def test_candidate_status_suppresses_preserved_marker_without_deleting_coordinates(status):
    from scripts.curated_export import integrate_curated_records
    from scripts.export_public_preview import preserve_map_relationships_after_integration
    from scripts.public_export_guard import analyze_shrinkage
    papers, markers, mappings, _, locations, _, _ = fixture()
    papers[0].update(authors='Ada Example', task='detection', scope_status='in_scope', curation_status='confirmed')
    original = deepcopy(locations)
    locations[0]['coordinate_status'] = status
    reviews = [dict(institution_id='institution:1', institution='Example University', related_paper_id='paper:1', review_status='pending_review', coordinate_status='needs_coordinate_review')]
    _, exported, _, _ = integrate_curated_records(papers, markers, papers, mappings, location_review_rows=reviews, confirmed_location_records=locations)
    assert not exported
    assert not preserve_map_relationships_after_integration(markers, exported, exclusion_rows=[], merge_rows=[], review_decisions=[], curated_mappings=mappings, location_rows=locations)
    report = analyze_shrinkage(papers, papers, markers, [], curated_mappings=mappings, location_rows=locations)
    assert report.allowed and all(r.explained for r in report.removed_maps)
    assert locations[0]['lat'] == original[0]['lat'] and locations[0]['lon'] == original[0]['lon']
    # Current reconfirmation supersedes the rejection; history is not a ban.
    locations[0]['coordinate_status'] = 'known'
    assert not ReviewedRelationshipResolver(mappings, locations=locations).supersedes(markers[0])
    _, exported, _, _ = integrate_curated_records(papers, [], papers, mappings, confirmed_location_records=locations)
    assert len(exported) == 1


def test_coordinate_rejection_is_scoped_to_location_not_other_campus():
    _, markers, mappings, _, locations, _, _ = fixture()
    locations[0]['coordinate_status'] = 'needs_coordinate_review'
    other = {**markers[0], 'location_id': 'location:other'}
    assert not ReviewedRelationshipResolver([], locations=locations).location_is_rejected(other)


def test_invalid_current_coordinates_cannot_preserve_old_valid_marker():
    _, markers, _, _, locations, _, _ = fixture()
    locations[0]['lat'] = 'nan'
    assert ReviewedRelationshipResolver([], locations=locations).location_is_rejected(markers[0])


def test_admin_confirmed_choices_exclude_retained_candidates():
    from scripts.curated_locations import location_review_payload
    from scripts.curated_mappings import load_mappings
    from scripts.paper_exclusions import read_exclusion_rows
    payload = location_review_payload(mappings=load_mappings(), exclusions=read_exclusion_rows())
    assert payload['summary']['confirmed_locations_count'] == len(payload['confirmed_locations']) == 456
    assert len(payload['candidate_locations']) == 4
    candidate_ids = {r['location_id'] for r in payload['candidate_locations']}
    assert not candidate_ids.intersection(r['location_id'] for r in payload['confirmed_locations'])
    assert all(valid_coordinates(r) and r['coordinate_status'] == 'needs_coordinate_review' for r in payload['candidate_locations'])
