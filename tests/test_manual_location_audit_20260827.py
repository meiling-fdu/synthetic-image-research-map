"""Durable regressions for the independently verified Admin location batch."""

import csv
import json
from pathlib import Path

import pytest

from scripts.curated_locations import location_review_payload, normalized_location_key
from scripts.curated_mappings import load_mappings
from scripts.paper_exclusions import read_exclusion_rows
from scripts.report_public_relationship_location_completeness import valid_coordinates
from scripts.validate_curated_database import validate_institution_entities

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data/curated"


def rows(name):
    with (CURATED / (name + ".csv")).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def locations(key):
    return [r for r in rows("institution_locations") if r["institution_id"] == "institution:" + key]


def markers(key):
    return [r for r in json.loads((ROOT / "web/data/public_preview_map_data.json").read_text())["records"] if r.get("institution_id") == "institution:" + key]


@pytest.mark.parametrize("key,city,lat,lon,rejected", [
    ("cc8345310a2617a6", "Durban", -29.852922926731402, 31.005967931251714, (-29.6458441, 30.3501321)),
    ("128d207ba007d9d7", "Dehradun", 30.2680182, 77.9961185, (30.2726626, 78.0003415)),
    ("d04d3d98b14dcbc7", "Bellville", -33.9318380, 18.6421452, (-33.9153709, 18.6339742)),
])
def test_corrected_campus_not_wrong_feature(key, city, lat, lon, rejected):
    location, = locations(key)
    assert location["city"] == city
    assert (float(location["lat"]), float(location["lon"])) == pytest.approx((lat, lon))
    current = [m for m in markers(key) if m.get("mapping_id")]
    assert current
    assert all((m["lat"], m["lon"]) != rejected for m in current)
    assert all((m["lat"], m["lon"]) == pytest.approx((lat, lon)) for m in current)


def test_graphic_era_and_hill_keep_distinct_identities_and_sites():
    assert locations("128d207ba007d9d7")[0]["lat"] != locations("803f64e5aa26f523")[0]["lat"]
    entities = {r["institution_id"]: r for r in rows("institutions")}
    for key in ("128d207ba007d9d7", "803f64e5aa26f523"):
        assert entities["institution:" + key]["institution_status"] == "active"


def test_deakin_two_campuses_and_exact_author_groups_not_bus_stop():
    campus = {r["city"]: r for r in locations("30e93da233b7eeef")}
    assert set(campus) == {"Burwood", "Waurn Ponds"}
    assert all((r["lat"], r["lon"]) != ("-37.8501813", "145.1151967") for r in campus.values())
    mappings = {r["institution_city"]: r for r in rows("author_institution_mappings") if r["paper_id"] == "curated:c071c25bc2957d78569b"}
    assert mappings["Burwood"]["institution_authors"] == "Thanh Thi Nguyen; Dung Tien Nguyen; Duc Thanh Nguyen"
    assert mappings["Waurn Ponds"]["institution_authors"] == "Cuong M. Nguyen; Saeid Nahavandi"
    assert {r["affiliation_order"] for r in mappings.values()} == {"1", "2"}
    for city, mapping in mappings.items():
        assert mapping["location_id"] == campus[city]["location_id"]
        exported = next(m for m in markers("30e93da233b7eeef") if m.get("mapping_id") == mapping["mapping_id"])
        assert exported["city"] == city
        assert exported["institution_authors"] == mapping["institution_authors"].split("; ")


def test_nirma_duplicate_consolidation_has_redirect_and_no_lost_mapping():
    location, = locations("af28dc8d805f8918")
    assert location["city"] == "Ahmedabad"
    audits = rows("institution_audit_log")
    assert any(r["action"] == "location_merge" and r["previous_location_id"] == "location:dec1e7f84933bb0b0327" and r["location_id"] == location["location_id"] for r in audits)
    assert len([r for r in rows("author_institution_mappings") if r["institution_id"] == location["institution_id"] and r["mapping_status"] == "active"]) == 2


def test_cuhk_merge_keeps_user_campus_alias_abbreviation_and_lineage():
    entities = {r["institution_id"]: r for r in rows("institutions")}
    survivor = "institution:ff4b6fb0e7e3f155"
    retired = "institution:5396ea72656b4b19"
    assert entities[survivor]["institution_status"] == "active"
    assert entities[retired]["institution_status"] == "merged"
    # Both pre-audit records had a blank structured abbreviation; preserve it.
    assert entities[survivor]["abbreviation"] == entities[retired]["abbreviation"] == ""
    assert any(r["alias_name"] == "The Chinese University of Hong Kong" and r["institution_id"] == survivor for r in rows("institution_aliases"))
    location, = locations("ff4b6fb0e7e3f155")
    assert (float(location["lat"]), float(location["lon"])) == (22.4201838, 114.2079145)
    assert not any(r["institution_id"] == retired and r["mapping_status"] in {"active", "needs_review"} for r in rows("author_institution_mappings"))
    assert any(r["action"] == "mapping_change_confirmed" and r["previous_location_id"] == "location:c64f284c57cab3a3fe18" and r["location_id"] == location["location_id"] and r["paper_id"] == "curated:084e01a1a2191cb4c86a" for r in rows("institution_audit_log"))


def test_retired_location_history_warns_but_active_reference_is_an_error():
    institution = {"institution_id": "institution:campus", "canonical_name": "Example University", "institution_status": "active"}
    location = {"institution_id": institution["institution_id"], "location_id": "location:current"}
    mapping = {"mapping_id": "mapping:campus", "paper_id": "paper:1", "institution_id": institution["institution_id"], "mapping_status": "active", "location_id": location["location_id"]}
    audit = {"action": "mapping_change_confirmed", "paper_id": "paper:1", "mapping_id": mapping["mapping_id"], "previous_institution_id": institution["institution_id"], "institution_id": institution["institution_id"], "previous_location_id": "location:retired", "location_id": location["location_id"]}
    issues = []
    validate_institution_entities([institution], [mapping], [location], [], [], [audit], issues)
    assert any(issue.level == "WARNING" and "previous_location_id: location:retired" in issue.message for issue in issues)
    assert not any(issue.level == "ERROR" for issue in issues)
    issues = []
    validate_institution_entities([institution], [{**mapping, "location_id": "location:retired"}], [location], [], [], [audit], issues)
    assert any(issue.level == "ERROR" and "unknown mapping-specific location_id: location:retired" in issue.message for issue in issues)


def test_all_supported_manual_decisions_survive_with_original_identity():
    audit = json.loads((ROOT / "docs/manual_institution_location_audit_2026-08-27.json").read_text())["manual_audit_set"]
    assert len(audit) == 16
    assert len({r["institution"]["institution_id"] for r in audit}) == 15
    current = {r["location_id"]: r for r in rows("institution_locations")}
    preserved = [r for r in audit if r["independent_review"]["action"] == "preserve"]
    assert len(preserved) == 7
    for item in preserved:
        old = item["selected_location"]
        assert current[old["location_id"]] == old


def test_five_supported_records_resolved_five_unresolved_no_headquarters():
    decisions = json.loads((ROOT / "docs/remaining_institution_location_audit_2026-08-27.json").read_text())
    payload = location_review_payload(mappings=load_mappings(), exclusions=read_exclusion_rows())
    assert payload["summary"]["pending_review"] == payload["summary"]["needs_coordinates"] == 5
    for decision in decisions:
        iid = decision["institution_id"]
        records = [r for r in payload["records"] if r["institution_id"] == iid]
        if decision["result"] == "confirmed":
            assert all(r["review_status"] in {"confirmed", "alias_of_confirmed"} for r in records)
            location, = locations(iid.split(":")[1])
            assert location["location_id"] == decision["location_id"]
            assert valid_coordinates(location)
        else:
            assert all(r["review_status"] == "pending_review" and r["evidence_source"] for r in records)
            assert not locations(iid.split(":")[1])
            assert not markers(iid.split(":")[1])
    jd = next(r for r in payload["records"] if r["institution_id"] == "institution:44469d661cb0034c")
    assert not jd["suggested_city"] and not jd["suggested_country"]
    assert "do not infer Beijing headquarters" in jd["evidence_source"]


def test_location_integrity_and_scoped_naming():
    locs = rows("institution_locations")
    assert all(valid_coordinates(r) for r in locs)
    assert len({r["location_id"] for r in locs}) == len(locs)
    assert len({normalized_location_key(r) for r in locs}) == len(locs)
    assert not any(r["country"] == "Türkiye" for r in locs)
    entities = {r["institution_id"]: r for r in rows("institutions")}
    assert entities["institution:bcd3d53e57c31275"]["canonical_name"] == "Mayachitra Inc."
    assert any(r["alias_name"] == "Mayachitra (United States)" and r["institution_id"] == "institution:bcd3d53e57c31275" for r in rows("institution_aliases"))
    assert entities["institution:1ee9da20656fd88b"]["canonical_name"] == "Politecnico di Milano"


def test_audited_legacy_centroid_markers_are_replaced_not_duplicated():
    audit = json.loads((ROOT / "docs/audited_marker_replacements_2026-08-27.json").read_text())
    exported = json.loads((ROOT / "web/data/public_preview_map_data.json").read_text())["records"]
    ids = {r["id"] for r in exported}
    assert len(audit["transitions"]) == 11
    for transition in audit["transitions"]:
        assert transition["previous_record_id"] not in ids
        assert any(r.get("mapping_id") == transition["mapping_id"] and r.get("location_id") == transition["location_id"] for r in exported)
