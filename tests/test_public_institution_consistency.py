import json
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.audit_public_institution_consistency import audit_consistency
from scripts.curated_export import (
    PaperIdentityCache, PaperIdentityIndex, enforce_affiliation_source_precedence,
    curated_affiliation_removal_reason, load_curated_mappings,
)
from scripts.export_public_preview import (
    add_paper_institution_search_ids, add_public_detail_fields, apply_ordered_paper_location_summaries,
    preserve_map_relationships_after_integration,
)
from scripts.public_export_guard import analyze_shrinkage


ROOT = Path(__file__).resolve().parents[1]
TITLE = "Diffusion Epistemic Uncertainty with Asymmetric Learning for Diffusion-Generated Image Detection"


def fixture():
    paper = {"paper_id": "paper:1", "title": "Example", "year": 2025,
             "authors": ["Ada Author", "Ben Author"]}
    mappings = [{**paper, "mapping_id": f"mapping:{i}", "mapping_status": "active",
                 "institution": f"University {i}", "institution_id": f"institution:{i}",
                 "institution_authors": "Ada Author; Ben Author" if i == 1 else "Ada Author",
                 "affiliation_order": i} for i in (1, 2)]
    markers = [{**m, "id": f"marker:{i}", "source_database": "curated",
                "institution_authors": m["institution_authors"].split("; ")}
               for i, m in enumerate(mappings)]
    return paper, mappings, markers


def test_active_set_replaces_historical_subsets_but_preserves_multiaffiliations():
    paper, mappings, markers = fixture()
    stale = {**markers[0], "id": "stale", "mapping_id": "",
             "institution": "Stale institution", "institution_id": "institution:stale",
             "institution_authors": ["Ada Author"], "source_database": "OpenAlex"}
    previous = [stale]
    enforce_affiliation_source_precedence([paper], markers, mappings)
    markers = preserve_map_relationships_after_integration(
        previous, markers, exclusion_rows=[], merge_rows=[], review_decisions=[],
        curated_mappings=mappings,
    )
    assert len(markers) == 2
    assert analyze_shrinkage([paper], [paper], previous, markers,
                            curated_mappings=mappings).allowed
    add_public_detail_fields([paper], markers)
    apply_ordered_paper_location_summaries([paper], markers)
    assert [a["affiliation_indices"] for a in paper["authors"]] == [[1, 2], [1]]
    assert audit_consistency([paper], markers, mappings)["mismatch_count"] == 0


def test_coalesced_same_site_marker_matches_union_of_active_mapping_authors():
    paper = {"paper_id": "paper:coalesced", "title": "Example", "year": 2025}
    mappings = [
        {
            **paper,
            "mapping_id": f"mapping:{index}",
            "mapping_status": "active",
            "institution": "Example University",
            "institution_id": "institution:example",
            "location_id": "location:example",
            "institution_authors": author,
        }
        for index, author in enumerate(("Ada Author", "Ben Author"), 1)
    ]
    marker = {
        **paper,
        "mapping_id": "mapping:1",
        "institution_id": "institution:example",
        "location_id": "location:example",
        "institution_authors": ["Ada Author", "Ben Author"],
    }

    assert curated_affiliation_removal_reason(marker, mappings) == ""


@pytest.mark.parametrize("status", ["excluded", "inactive", "superseded"])
def test_historical_only_curation_is_reviewed_empty(status):
    paper, mappings, markers = fixture()
    for row in mappings:
        row["mapping_status"] = status
    previous = deepcopy(markers)
    enforce_affiliation_source_precedence([paper], markers, mappings)
    assert not markers
    assert not preserve_map_relationships_after_integration(
        previous, markers, exclusion_rows=[], merge_rows=[], review_decisions=[],
        curated_mappings=mappings,
    )
    add_public_detail_fields([paper], markers)
    apply_ordered_paper_location_summaries([paper], markers)
    assert paper["affiliations"] == []
    assert audit_consistency([paper], markers, mappings)["mismatch_count"] == 0
    assert analyze_shrinkage([paper], [paper], previous, [], curated_mappings=mappings).allowed


def test_candidates_do_not_block_fallback_and_active_members_cannot_disappear():
    paper, mappings, markers = fixture()
    # A valid active curated relationship remains protected by the guard.
    assert not analyze_shrinkage([paper], [paper], markers, [], curated_mappings=mappings).allowed
    for row in mappings:
        row["mapping_status"] = "needs_review"
    assert preserve_map_relationships_after_integration(
        markers, [], exclusion_rows=[], merge_rows=[], review_decisions=[],
        curated_mappings=mappings,
    ) == markers


def test_details_ignore_stale_derived_affiliations_and_author_assignments():
    paper, mappings, markers = fixture()
    enforce_affiliation_source_precedence([paper], markers, mappings)
    stale = {**markers[0], "id": "old", "institution_id": "institution:old",
             "institution": "Old", "mapping_id": "old",
             "author_institution_affiliations": [
                 {"institution_id": "institution:old", "institution": "Old", "authors": ["Ben Author"]},
                 {"institution_id": "institution:2", "institution": "University 2", "authors": ["Ben Author"]},
             ]}
    for _ in range(2):  # Repeated detail enrichment must be idempotent.
        add_public_detail_fields([paper], [*markers, stale])
        assert {a["institution_id"] for a in paper["affiliations"]} == {"institution:1", "institution:2"}
        assert [a["affiliation_indices"] for a in paper["authors"]] == [[1, 2], [1]]


def test_coordinate_less_mapping_keeps_its_persisted_id_and_summary_membership():
    paper, mappings, markers = fixture()
    markers.pop()
    enforce_affiliation_source_precedence([paper], markers, mappings)
    add_public_detail_fields([paper], markers)
    apply_ordered_paper_location_summaries([paper], markers)
    assert audit_consistency([paper], markers, mappings)["mismatch_count"] == 0


def test_active_curation_excludes_pending_history_and_stale_search_ids():
    paper, mappings, markers = fixture()
    mappings.append({**mappings[0], "mapping_id": "candidate", "mapping_status": "needs_review",
                     "institution_id": "institution:candidate", "institution": "Candidate"})
    paper["search_institution_ids"] = ["institution:stale"]
    enforce_affiliation_source_precedence([paper], markers, mappings)
    add_paper_institution_search_ids([paper], mappings, {"institution:1": "institution:alias"})
    assert paper["search_institution_ids"] == ["institution:1", "institution:2"]
    add_public_detail_fields([paper], markers)
    assert len(paper["affiliations"]) == 2


def test_unreviewed_mixed_affiliations_keep_pending_evidence_out_of_markers():
    paper, mappings, markers = fixture()
    paper.update(curation_status="needs_review", review_status="pending")
    pending = {**mappings[0], "mapping_id": "candidate", "mapping_status": "needs_review",
               "institution_id": "institution:candidate", "institution": "Candidate",
               "institution_authors": "Ben Author", "raw_affiliation": "Candidate University",
               "provenance_source": "https://example.org/paper.pdf"}
    mappings.append(pending)
    enforce_affiliation_source_precedence([paper], markers, mappings)
    add_public_detail_fields([paper], markers)
    apply_ordered_paper_location_summaries([paper], markers)
    assert {a["institution_id"] for a in paper["affiliations"]} == {
        "institution:1", "institution:2", "institution:candidate"
    }
    assert {m["institution_id"] for m in markers} == {"institution:1", "institution:2"}
    assert next(a for a in paper["affiliations"] if a["institution_id"] == "institution:candidate")["preliminary"]
    affiliation_names = {a["index"]: a["name"] for a in paper["affiliations"]}
    ben = next(author for author in paper["authors"] if author["name"] == "Ben Author")
    assert [affiliation_names[index] for index in ben["affiliation_indices"]] == [
        "University 1", "Candidate"
    ]
    assert audit_consistency([paper], markers, mappings)["mismatch_count"] == 0


@pytest.mark.parametrize("field", ["affiliations", "author_institution_affiliations", "authors", "marker", "aggregated_locations"])
def test_audit_detects_corruption_in_each_display_source(field):
    paper, mappings, markers = fixture()
    enforce_affiliation_source_precedence([paper], markers, mappings)
    add_public_detail_fields([paper], markers)
    apply_ordered_paper_location_summaries([paper], markers)
    if field == "authors":
        paper["author_institution_affiliations"][1]["authors"] = ["Ben Author"]
    elif field == "marker":
        markers[0]["mapping_id"] = "retired"
    else:
        paper[field].pop()
    assert audit_consistency([paper], markers, mappings)["mismatch_count"] == 1


def test_all_public_curated_papers_and_markers_match_effective_mappings():
    papers = json.loads((ROOT / "web/data/public_preview_papers.json").read_text())["records"]
    markers = json.loads((ROOT / "web/data/public_preview_map_data.json").read_text())["records"]
    report = audit_consistency(papers, markers, load_curated_mappings())
    assert report["states"]["curated"] > 300
    assert report["mismatch_count"] == 0, report["mismatches"]


def test_diffusion_epistemic_exact_institutions_and_authors():
    papers = json.loads((ROOT / "web/data/public_preview_papers.json").read_text())["records"]
    paper = next(p for p in papers if p["title"] == TITLE)
    mappings = PaperIdentityIndex(load_curated_mappings(), PaperIdentityCache()).matches(paper)
    expected = {"Tencent Inc.": ["Yingsong Huang", "Hui Guo", "Qi Xiong"],
                "Hikvision": ["Jing Huang"], "Microsoft": ["Bing Bai"]}
    assert {m["institution"] for m in mappings if m["mapping_status"] == "active"} == set(expected)
    assert {a["institution"]: a["authors"] for a in paper["author_institution_affiliations"]} == expected
    assert len(paper["affiliations"]) == 3
    indices = {a["index"]: a["name"] for a in paper["affiliations"]}
    assert {a["name"]: [indices[i] for i in a["affiliation_indices"]] for a in paper["authors"]} == {
        author: [institution] for institution, authors in expected.items() for author in authors
    }


def test_production_frontend_normalizer_matches_every_curated_paper():
    """Execute the actual static frontend with both paper and marker inputs."""
    app = (ROOT / "web/app.js").read_text()
    names = ["normalizePaperDetailsRecord", "affiliationIdentity", "institutionIdentity",
             "recordInstitution", "recordInstitutionAuthors", "normalizedAuthorName",
             "matchingAuthorMapValue", "uniqueTextValues", "normalizeInstitutionType",
             "recordLocation", "normalizeCountryRegionRecord", "normalizedLocationName",
             "normalizedTitle", "normalizedDoi", "normalizedIdentityValue", "paperIdentity",
             "recordPaperUrl", "recordTitle", "normalizedSearchText",
             "buildCanonicalInstitutionResolver", "canonicalizeInstitutionObject",
             "canonicalizePublicDataset", "orderedPaperLocationSummary"]
    functions = "\n".join(
        "function " + name + "(" + app.split("function " + name + "(", 1)[1].split("\nfunction ", 1)[0]
        for name in names
    )
    node = Path("/Users/meilinger/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node")
    script = r"""
const fs = require('fs');
const root = process.argv[1];
const PaperDetailsHelpers = require(root + '/web/paper_details_helpers.js');
const InstitutionDisplay = require(root + '/web/institution_display.js');
const InstitutionTypeLabels = require(root + '/web/institution_type_labels.js');
const CHINA_REGION_BY_CODE = {HK: 'Hong Kong', MO: 'Macao', TW: 'Taiwan'};
const CHINA_REGION_CODE_BY_NAME = {'hong kong': 'HK', macao: 'MO', taiwan: 'TW'};
const COUNTRY_NAME_BY_CODE = {};
""" + functions + r"""
const payload = JSON.parse(fs.readFileSync(root + '/web/data/public_preview_papers.json'));
const mapPayload = JSON.parse(fs.readFileSync(root + '/web/data/public_preview_map_data.json'));
const dataset = canonicalizePublicDataset(mapPayload.records, payload.records,
  payload.institution_aliases, payload.canonical_institution_search_index, payload.institution_id_redirects);
const papers = dataset.paperRecords;
const markers = dataset.mapRecords;
let checked = 0;
for (const paper of papers.filter(p => p.affiliation_review_state === 'curated')) {
  const related = markers.filter(m => paper.paper_id ? m.paper_id === paper.paper_id : m.title === paper.title);
  const visibleMappings = paper.curated_mappings.filter(m => m.mapping_status === 'active'
    || (paper.curation_status === 'needs_review' && m.mapping_status === 'needs_review'));
  const expected = [...new Set(visibleMappings.map(m => m.institution_id))].sort();
  const summaryIds = paper.aggregated_locations.map(a => a.institution_id).sort();
  if (JSON.stringify(expected) !== JSON.stringify(summaryIds)) throw new Error(paper.title + ': summary mismatch');
  for (const source of [paper, ...related]) {
    const normalized = normalizePaperDetailsRecord(source, {relatedRecords: [paper, ...related]});
    const actual = normalized.affiliations.map(a => a.institutionId).sort();
    if (JSON.stringify(expected) !== JSON.stringify(actual)) throw new Error(paper.title);
    for (const affiliation of normalized.affiliations) {
      const expectedAuthors = [...new Set(visibleMappings
        .filter(m => m.institution_id === affiliation.institutionId)
        .flatMap(m => m.institution_authors))].sort();
      if (JSON.stringify(affiliation.authors.slice().sort()) !== JSON.stringify(expectedAuthors)) {
        throw new Error(paper.title + ': affiliation author mismatch');
      }
    }
    if (paper.title.startsWith('Diffusion Epistemic')) {
      const assignments = Object.fromEntries(normalized.authors.map(a => [a.name,
        a.affiliation_indices.map(i => normalized.affiliations[i - 1].institution)]));
      if (JSON.stringify(assignments['Qi Xiong']) !== '["Tencent Inc."]') throw new Error('Qi Xiong assignment');
      const markup = PaperDetailsHelpers.renderPaperAuthors(normalized, String);
      if (!markup.includes('Qi Xiong')) throw new Error('Missing rendered author');
    }
    checked++;
  }
}
process.stdout.write(JSON.stringify({checked}));
"""
    result = subprocess.run([str(node), "-e", script, str(ROOT)],
                            check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["checked"] > 1000
