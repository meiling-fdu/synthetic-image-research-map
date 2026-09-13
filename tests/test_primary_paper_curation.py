"""Primary evidence must survive export, without changing older curation."""
import copy
import hashlib
import json

import pytest

from scripts import report_primary_paper_curation as audit
from scripts.curated_export import _merge_curated_paper, _mark_location_known
from scripts.export_public_preview import preserve_existing_curation_status
from scripts.public_metadata_status import add_public_metadata_status
from scripts.paper_exclusions import exclusions_with_curated_identities, filter_public_output_pair


def test_current_curation_audit_reproduces_and_preserves_every_older_row():
    report = audit.build_audit()
    assert report['integrity']['pre_existing_changes'] == []
    assert report['summary']['public_papers'] == 620
    assert report['summary']['taxonomy_reviewed'] == 10
    assert report['summary']['affiliation_reviewed'] == 9
    assert report['summary']['fully_curated'] == 7
    assert report['summary']['marker_bearing'] == 6
    assert len(report['summary']['excluded']) == 3
    for suffix, text in audit.render(report).items():
        assert (audit.ROOT / (str(audit.OUTPUT) + suffix)).read_text() == text


def test_undefined_secondary_affiliation_is_not_filled_by_coauthor_or_web_inference():
    ledger = json.loads((audit.ROOT / audit.LEDGER).read_text())
    provenance = next(d for d in ledger['papers'] if d['key'] == '2503.11195')
    assert provenance['affiliation_status'] == 'needs_review'
    assert provenance['curation_status'] == 'needs_review'
    assert any('superscripts 1,2' in text for text in provenance['unresolved_fields'])
    for author in ('Shree Singhi', 'Aayan Yadav'):
        assert [a['institution'] for a in provenance['affiliations'] if author in a['authors']] == ['Zellic']
    assert not any(i['name'].startswith('Indian Institute') for i in ledger['institutions'])


def test_dataset_benchmark_and_manipulation_domains_have_full_text_evidence():
    ledger = json.loads((audit.ROOT / audit.LEDGER).read_text())
    decisions = {d['key']: d for d in ledger['papers']}
    assert decisions['2510.05740']['research_types'] == ['method', 'dataset', 'benchmark']
    assert decisions['safe']['research_types'] == ['dataset', 'benchmark']
    assert decisions['2510.23023']['image_scopes'] == ['fully_generated', 'generative_editing', 'deepfake']
    assert decisions['2512.20257']['tasks'] == ['detection']
    for d in decisions.values():
        assert (audit.ROOT / d['primary_pdf']).read_bytes().startswith(b'%PDF')
        assert all(d['taxonomy_evidence'][dimension] for dimension in audit.DIMENSIONS)


def test_cached_primary_sources_match_the_immutable_manifest():
    folder = audit.ROOT / 'data/raw/primary_curation_2026_09_08'
    manifest = json.loads((folder / 'manifest.json').read_text())
    for entry in manifest['files']:
        content = (folder / entry['path']).read_bytes()
        assert len(content) == entry['bytes']
        assert hashlib.sha256(content).hexdigest() == entry['sha256']


def test_current_reconciliation_counts_existing_exclusions_instead_of_missing_papers():
    from scripts.verify_key_paper_reconciliation import verify_current_curation
    report = verify_current_curation()
    totals = report['final_audit']
    assert totals['bibliography_covered'] == 287
    assert totals['covered_as_map_marker'] == 286
    assert totals['covered_in_public_preview_paper_list'] == 1
    assert totals['excluded'] == 10
    assert totals['possible_title_match_failure'] == 2
    for row in report['exclusion_identity_traces']:
        assert row['exclusion_effective_date'].startswith('2026-07-13')
        assert row['exclusion_match_identity'].startswith('openalex:')
        assert row['membership_state'] == 'CURATED_BUT_EXCLUDED'


@pytest.mark.parametrize('curation,review', [('confirmed', 'reviewed'), ('needs_review', 'needs_check')])
def test_exact_id_review_survives_new_external_identity_and_stale_public_snapshot(curation, review):
    original = dict(paper_id='curated:example', title='Old title', year=2025,
                    curation_status='needs_review', review_status='pending',
                    metadata_source='arxiv', openalex_url='')
    older = dict(original, paper_id='curated:older', title='Unrelated paper')
    records = [copy.deepcopy(original), copy.deepcopy(older)]
    curated = dict(original, title='Reviewed title', curation_status=curation,
                   review_status=review, metadata_source='Primary-source review 2026-09-08: https://arxiv.org/abs/2506.11031',
                   openalex_url='https://openalex.org/W4415314077', authors='Author One',
                   arxiv_id='2506.11031', tasks='detection', image_scopes='fully_generated',
                   research_types='method', publication_type='preprint', venue='arXiv')
    _merge_curated_paper(records[0], curated)
    preserve_existing_curation_status(records, [original, older])
    assert records[0]['curation_status'] == curation
    assert records[0]['review_status'] == review
    assert records[0]['title'] == 'Reviewed title'
    assert records[0]['openalex_url'] == curated['openalex_url']
    assert records[1] == older
    add_public_metadata_status(records, [])
    assert records[0]['metadata_status']['overall'] == ('Verified' if review == 'reviewed' else 'Needs review')
    assert records[0]['metadata_source'] == curated['metadata_source']
    assert records[0]['publication_type'] == 'preprint'


def test_pending_automatic_metadata_does_not_override_an_existing_curated_decision():
    record = dict(paper_id='curated:x', curation_status='confirmed', title='Reviewed original')
    before = copy.deepcopy(record)
    _merge_curated_paper(record, dict(paper_id='curated:x', curation_status='needs_review',
                                    metadata_source='arxiv', title='Automatic candidate'))
    assert record['curation_status'] == before['curation_status']
    assert record['title'] == before['title']


def test_legacy_manual_provenance_remains_preserved_during_refresh():
    previous = dict(paper_id='curated:older', title='Reviewed paper',
                    curation_status='corrected_by_admin', review_status='reviewed',
                    metadata_source='openalex')
    current = dict(previous, curation_status='confirmed')
    preserve_existing_curation_status([current], [previous])
    assert current == previous


def test_verified_identity_cannot_revive_an_existing_exclusion_from_a_stale_preview():
    old = dict(paper_id='curated:provenance', title='Provenance Detection', year=2025,
               arxiv_id='2503.11195', openalex_url='')
    unrelated = dict(old, paper_id='curated:different', arxiv_id='2503.99999')
    curated = dict(old, openalex_url='https://openalex.org/W4417284156')
    exclusion = dict(exclusion_id='existing', openalex_url=curated['openalex_url'],
                     title=old['title'], year=2025, is_active='true')
    original = copy.deepcopy(exclusion)
    effective = exclusions_with_curated_identities([exclusion], [curated, unrelated])
    papers, markers, summary = filter_public_output_pair([old, unrelated], [old], effective)
    assert papers == [unrelated]
    assert markers == []
    assert summary['active_exclusion_public_papers_removed'] == 1
    assert exclusion == original
    restored = dict(exclusion, is_active='false')
    effective = exclusions_with_curated_identities([restored], [curated])
    assert filter_public_output_pair([old], [], effective)[0] == [old]


@pytest.mark.parametrize('status', ['pending_review', 'ambiguous', 'needs_review'])
def test_export_does_not_promote_a_pending_paper_specific_location_review(status):
    row = dict(institution_id='institution:example', related_paper_id='curated:example',
               institution='Example University', title='Example paper', year='2025',
               review_status=status, location_status='missing', coordinate_status='missing',
               updated_at='2026-09-06T00:00:00Z')
    rows = [copy.deepcopy(row)]
    mapping = dict(institution_id='institution:example', paper_id='curated:example',
                   institution='Example University', title='Example paper', year='2025')
    assert not _mark_location_known(rows, mapping)
    assert rows == [row]
