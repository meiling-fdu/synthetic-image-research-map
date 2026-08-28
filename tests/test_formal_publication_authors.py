"""Formal author blocks outrank preprint/project data in canonical exports."""
import csv
import json
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.curated_export import integrate_curated_records
from scripts.export_public_preview import add_public_detail_fields
from scripts.formal_author_curation import plan_formal_authors
from scripts.report_missing_author_mappings import build_report_rows

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://example.org/proceedings/final.pdf"


def fixture():
    paper = dict(paper_id="paper:formal-test", title="Formal fixture", year="2026",
                 authors="Ada; Preprint Only; Bob", task="detection",
                 scope_status="in_scope", curation_status="confirmed",
                 publication_type="conference", metadata_source="preprint")
    mappings = [dict(paper_id=paper["paper_id"], title=paper["title"], year="2026",
                     mapping_id=f"mapping:{i}", institution=f"University {i}",
                     institution_id=f"institution:{i}", institution_authors=names,
                     mapping_status="active", affiliation_order=str(i),
                     raw_affiliation=f"University {i}", author_order="")
                for i, names in [(1, "Ada; Bob"), (2, "Preprint Only")]]
    return paper, mappings


def plan(paper, mappings, matrix, kind="formal_publication"):
    return plan_formal_authors(paper, mappings, matrix,
                              evidence_url=SOURCE, source_kind=kind)


def export(paper, mappings, matrix):
    result = plan(paper, mappings, matrix)
    final = {**paper, "authors": "; ".join(result["authors"]),
             "metadata_source": "Formal publication: " + SOURCE}
    papers, markers, _, _ = integrate_curated_records(
        [paper], [], [final], result["mappings"])
    add_public_detail_fields(papers, markers)
    return result, papers, markers


def test_increfa_equivalent_formal_roster_removes_preprint_only_warning():
    paper, mappings = fixture()
    before = deepcopy((paper, mappings))
    matrix = [dict(index=i, name=n, mapping_ids=["mapping:1"])
              for i, n in enumerate(["Ada", "Bob"], 1)]
    result, papers, markers = export(paper, mappings, matrix)
    assert [a["name"] for a in papers[0]["authors"]] == ["Ada", "Bob"]
    row, = build_report_rows(papers, markers, [], result["mappings"], [])
    assert row["missing_authors"] == 0
    assert result["mappings"][1]["mapping_status"] == "excluded"
    assert result["mappings"][1]["institution_authors"] == "Preprint Only"
    assert (paper, mappings) == before  # historical discrepancy remains available


def test_formal_order_reindexes_by_explicit_occurrence_not_old_position():
    paper, mappings = fixture()
    result = plan(paper, mappings, [
        dict(index=1, name="Bob", mapping_ids=["mapping:1"]),
        dict(index=2, name="Ada", mapping_ids=["mapping:1"])])
    assert result["mappings"][0]["institution_authors"] == "Bob; Ada"
    assert result["mappings"][0]["author_order"] == "1; 2"


def test_formal_multiple_superscripts_preserve_both_institutions():
    paper, mappings = fixture()
    result, papers, _ = export(paper, mappings, [
        dict(index=1, name="Ada", mapping_ids=["mapping:1", "mapping:2"]),
        dict(index=2, name="Bob", mapping_ids=["mapping:1"])])
    assert papers[0]["authors"][0]["affiliation_indices"] == [1, 2]
    assert result["mappings"][1]["author_order"] == "1"


def test_project_affiliation_cannot_override_verified_formal_mapping():
    paper, mappings = fixture()
    paper.update(metadata_source="official project", authors=[
        dict(name="Ada", affiliation_indices=[1])],
        affiliations=[dict(index=1, institution="Wrong project institution")])
    _, papers, _ = export(paper, mappings, [
        dict(index=1, name="Ada", mapping_ids=["mapping:1"])])
    assert "Wrong project institution" not in json.dumps(papers[0]["affiliations"])
    assert papers[0]["authors"][0]["affiliation_indices"] == [1]


@pytest.mark.parametrize("kind", ["preprint", "project", "openalex"])
def test_lower_tier_source_cannot_authorize_formal_plan(kind):
    paper, mappings = fixture()
    with pytest.raises(ValueError, match="formal publication"):
        plan(paper, mappings, [], kind)


@pytest.mark.parametrize("matrix", [[],
    [dict(index=2, name="Ada", mapping_ids=["mapping:1"])],
    [dict(index=1, name="Ada", mapping_ids=["mapping:unrelated"])],
    [dict(index=1, name="Ada", mapping_ids=["mapping:1", "mapping:1"])],
    [dict(index=1, name="Ada", mapping_ids=[])],
])
def test_invalid_matrix_fails_before_any_write(matrix):
    paper, mappings = fixture()
    before = deepcopy((paper, mappings))
    with pytest.raises(ValueError):
        plan(paper, mappings, matrix)
    assert (paper, mappings) == before


def test_repository_formal_rosters_and_mapping_positions():
    audit = json.loads((ROOT / "docs/formal_publication_audit_2026-08-27.json").read_text())
    papers = json.loads((ROOT / "web/data/public_preview_papers.json").read_text())["records"]
    mappings = list(csv.DictReader((ROOT / "data/curated/author_institution_mappings.csv").open()))
    for case in audit["formal_papers"]:
        paper = next(p for p in papers if p.get("paper_id") == case["paper_id"])
        expected = [r["name"] for r in case["matrix"]]
        assert [a["name"] for a in paper["authors"]] == expected
        for m in mappings:
            if m["paper_id"] == case["paper_id"] and m["mapping_status"] == "active":
                assert [expected[int(i)-1] for i in m["author_order"].split("; ")] == m["institution_authors"].split("; ")
    increfa = next(p for p in papers if p["title"].startswith("IncreFA:"))
    assert len(increfa["authors"]) == 5 and increfa["affiliation_complete"]
    omni = next(p for p in papers if p["title"].startswith("Omni-Fake:"))
    assert omni["authors"][11]["name"] == "Xiangtai Li"
    assert omni["authors"][11]["affiliation_indices"] == [4]


def test_admin_candidates_preserved_but_only_verified_locations_export():
    audit = json.loads((ROOT / "docs/formal_publication_audit_2026-08-27.json").read_text())
    locations = list(csv.DictReader((ROOT / "data/curated/institution_locations.csv").open()))
    markers = json.loads((ROOT / "web/data/public_preview_map_data.json").read_text())["records"]
    for case in audit["manual_locations"]:
        submitted = case["submitted_location"]
        final = next(l for l in locations if l["location_id"] == submitted["location_id"])
        assert final == case["final_location"]
        assert final["created_at"] == submitted["created_at"]
        assert final["created_by"] == submitted["created_by"]
        exported = [m for m in markers if m.get("institution_id") == case["institution_id"]]
        if case["accepted"]:
            assert final["lat"] == submitted["lat"]
            assert final["lon"] == "-122.05238"
            assert exported and all(float(m["lon"]) == -122.05238 for m in exported)
        else:
            assert (final["lat"], final["lon"]) == (submitted["lat"], submitted["lon"])
            assert final["coordinate_status"] == "needs_coordinate_review"
            assert not exported


def test_formal_journal_expansion_rebuilds_five_to_nine_positions():
    audit = json.loads((ROOT / 'docs/formal_publication_audit_2026-08-27.json').read_text())
    case = next(c for c in audit['formal_papers'] if c['paper_id'] == 'curated:c071c25bc2957d78569b')
    rows = list(csv.DictReader((ROOT / 'data/curated/institution_audit_log.csv').open()))
    event = next(a for a in rows if a['paper_id'] == case['paper_id'] and a['action'] == 'formal_publication_roster_applied')
    proof = json.loads(event['confirmation_text'])
    assert len(proof['previous_paper']['authors'].split('; ')) == 5
    assert len(proof['final_paper']['authors'].split('; ')) == 9
    result = plan(proof['previous_paper'], proof['final_mappings'], proof['matrix'])
    by_id = {r['mapping_id']: r for r in result['mappings']}
    assert by_id['mapping:deakin-waurn-ponds-20260827']['institution_authors'] == 'Saeid Nahavandi'
    assert by_id['mapping:deakin-waurn-ponds-20260827']['author_order'] == '6'
    cuong = next(m for m in result['mappings'] if m['institution_authors'] == 'Cuong M. Nguyen')
    assert cuong['author_order'] == '9'
    assert cuong['institution_id'] == 'institution:1e2fe2432a089705'
    from scripts.public_relationships import ReviewedRelationshipResolver
    old = proof['previous_mappings'][1]
    resolver = ReviewedRelationshipResolver(proof['final_mappings'], [event])
    assert resolver.supersedes(old)
    assert not resolver.supersedes(by_id[old['mapping_id']])
    for field in ['paper_id', 'doi', 'institution_id', 'location_id', 'institution_authors']:
        assert not resolver._formal_replacement_mapping_ids({**old, field: 'unrelated'})
    for field in ['author_order', 'institution_authors', 'doi', 'institution_id', 'location_id']:
        bad = deepcopy(proof['final_mappings'])
        bad[0][field] = 'unrelated'
        assert not ReviewedRelationshipResolver(bad, [event])._formal_replacement_mapping_ids(old)
    assert not ReviewedRelationshipResolver(proof['final_mappings'][1:], [event])._formal_replacement_mapping_ids(old)


def test_final_volume_year_and_formal_rosters_survive_lower_tier_export_inputs():
    papers = list(csv.DictReader((ROOT / 'data/curated/papers.csv').open()))
    for pid, count in [('curated:246f07c81b9f91e527eb', 5), ('curated:fe42bad5f72f9f6858c5', 13), ('curated:c071c25bc2957d78569b', 9), ('curated:6e6c7c4645ed4af43a61', None)]:
        formal = next(p for p in papers if p['paper_id'] == pid)
        lower = {**formal, 'authors': 'Preprint Only', 'year': '2020', 'metadata_source': 'project/BibTeX/preprint'}
        for _ in range(2):
            exported, _, _, _ = integrate_curated_records([lower], [], [formal], [])
            assert exported[0]['authors'] == formal['authors'].split('; ')
            assert str(exported[0]['year']) == formal['year']
            if count:
                assert len(exported[0]['authors']) == count
            else:
                assert formal['year'] == '2025'
            lower = exported[0]
