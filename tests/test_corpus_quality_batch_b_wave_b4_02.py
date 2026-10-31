"""B4-02 accepts three journal bindings and keeps twelve explicit holds.

Current decisions are located by native ID. Transaction accounting uses the
immutable baseline plus this packet, so later integration of independent B4-01
rows cannot move or alter this historical accounting endpoint.
"""
from collections import Counter
from copy import deepcopy
import csv
from functools import lru_cache
import hashlib
import io
import json
from pathlib import Path
import re

import pytest

from scripts.curated_schema import INSTITUTION_LOCATION_COLUMNS
from scripts.curated_locations import (
    CuratedLocationError, _confirmed_location_fields, is_confirmed_location,
)
from scripts.review_decisions import read_review_decisions, upsert_review_decision
from scripts.validate_corpus_quality_audit import decision_rows, load_context, load_queues
from scripts.venue_audit import VenueAudit, confirmation_fingerprint
from scripts.venues import canonical_venue_registry, read_venue_aliases
from tests.corpus_quality_test_helpers import csv_records, published_bytes, published_context

ROOT = Path(__file__).resolve().parents[1]
BASE = '7fc8ceae702324628335944cf4b545a3733fdc56'
MANIFEST = 'data/raw/corpus_quality_batch_b_wave_b4_02_2026_10_29/adjudication_manifest.json'
PAPERS = 'data/curated/papers.csv'
ALIASES = 'data/curated/venue_aliases.csv'
DECISIONS = 'data/curated/review_decisions.csv'
ASSIGNED = ['P001', 'U001', 'U002', 'U003', 'P049', 'U005', 'P058', 'U006',
            'U007', 'P068', 'U008', 'U014', 'U016', 'U018', 'U023']
ACCEPTED = ['P049', 'P058', 'P068']
HELD = [rid for rid in ASSIGNED if rid not in ACCEPTED]
BIBLIOGRAPHIC_FIELDS = ('title', 'year', 'authors', 'doi', 'arxiv_id', 'openalex_url')
NATIVE_FIELDS = ('review_queue', 'target_type', 'doi', 'openalex_url', 'title', 'year', 'institution')
# Reserve the other pending transaction's native identities without importing
# or requiring its unpublished checkout or manifest on a test runner.
B4_01_RESERVED_IDS = {
    'review:4f3e2bcbf2d0294c6118',
    'review:5445762b46f00e76c3c6',
    'review:5464d1c1552b94847682',
    'review:8aa8f164a0591cc84b0c',
    'review:905c181f62686fdd1d46',
    'review:908428d376d858278016',
    'review:a1eb8fea1c6f117dbf96',
    'review:c5a66f0b4a9e8c9a1135',
    'review:d0be82c0d01fb23f6dec',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def object_sha(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())


@lru_cache
def packet():
    return json.loads((ROOT / MANIFEST).read_text())


def case(rid):
    found = [r for r in packet()['records'] if r['review_id'] == rid]
    assert len(found) == 1
    return found[0]


def source_row(rid):
    pid = case(rid)['paper_id']
    found = [r for r in read_rows(PAPERS) if r['paper_id'] == pid]
    assert len(found) == 1
    return found[0]


def read_rows(path):
    with (ROOT / path).open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def native_id(decision):
    identity = '|'.join(' '.join(str(decision.get(k, '')).split()).casefold() for k in NATIVE_FIELDS)
    return 'review:' + sha(identity.encode())[:20]


def acceptance_valid(record, decision, source):
    """Bounded decision acceptance, including holds that must never close.

    A hash in a note alone is insufficient: the accepted source identity and
    venue fields must still agree with the independently reviewed binding.
    """
    binding = record['binding']
    note = decision.get('review_note', '')
    accepted = record['review_id'] in ACCEPTED
    bib = binding['bibliographic_identity']
    if not all((
        record['accepted'] is accepted,
        decision.get('decision_id') == record['native_id'] == native_id(decision),
        decision.get('review_queue') == ('publication_venues' if record['review_id'].startswith('P') else 'marker_blocker'),
        decision.get('target_type') == 'paper',
        decision.get('created_by') == 'maintainer-approved-batch-b-b4-02',
        decision.get('action') == ('no_action_after_review' if accepted else 'unresolved'),
        all(decision.get(k) == bib[k] for k in ('title', 'year', 'doi', 'openalex_url')),
        source['paper_id'] == binding['paper_id'] == record['paper_id'],
        all(source.get(k) == bib[k] for k in BIBLIOGRAPHIC_FIELDS),
        binding['review_id'] == record['review_id'],
        binding['baseline_commit'] == BASE,
        binding['original_question'] == record['b3_evidence_record']['original_review_question'],
        binding['b3_matrix_sha256'] == packet()['b3_input_sha256']['batch_dispositions.json'],
        re.fullmatch(r'[a-f0-9]{64}', binding['b3_paper_record_sha256']) is not None,
        note.startswith('Batch B review ' + record['review_id'] + ';'),
        record['binding_sha256'] == object_sha(binding),
        '[b4-02-state:' + record['binding_sha256'] + ']' in note,
        binding['b3_matrix_sha256'] in note,
        binding['b3_paper_record_sha256'] in note,
    )):
        return False
    if record['review_id'].startswith('P'):
        fingerprint = confirmation_fingerprint(source)
        if not (binding['venue_state_fingerprint'] == fingerprint
                and '[venue-state:' + fingerprint + ']' in note):
            return False
    elif '[venue-state:' in note or binding['venue_state_fingerprint'] is not None:
        return False
    if accepted:
        expected = binding['accepted_venue_fields']
        return (record['disposition'] == 'CANONICAL_JOURNAL_BINDING_ACCEPTED'
                and set(expected) == {'venue_id', 'venue_name', 'venue_type'}
                and all(source.get(k) == v for k, v in expected.items())
                and source['venue_type'] == source['publication_type'] == 'journal'
                and source['venue_acronym'] == source['venue_track'] == '')
    return binding['accepted_venue_fields'] is None


def terminal(rows):
    result = {}
    special = {'review:b9f458d69de24b8aae0a': 'R267', 'review:aa32e93a24ade10ed99d': 'R236'}
    for row in rows:
        if row['action'] != 'no_action_after_review':
            continue
        match = re.search(r'\bBatch B review ([A-Z]\d{3});', row['review_note'])
        rid = match[1] if match else special.get(row['decision_id'])
        if rid:
            assert rid not in result, 'Duplicate terminal decision for an original review'
            result[rid] = row
    return result


def test_exact_assigned_coverage_three_acceptances_and_twelve_holds():
    records = packet()['records']
    assert [r['review_id'] for r in records] == ASSIGNED
    assert len({r['paper_id'] for r in records}) == 11
    assert [r['review_id'] for r in records if r['accepted']] == ACCEPTED
    assert [r['review_id'] for r in records if not r['accepted']] == HELD
    assert packet()['accepted_review_ids'] == ACCEPTED
    assert packet()['held_review_ids'] == HELD
    assert packet()['baseline_commit'] == BASE
    assert packet()['exports_run'] == packet()['source_retrievals'] == packet()['geocoding_requests'] == 0


@pytest.mark.parametrize('rid', ASSIGNED)
def test_live_formal_decision_is_unique_native_and_evidence_bound(rid):
    record = case(rid)
    found = [r for r in read_review_decisions() if r['decision_id'] == record['native_id']]
    assert found == [record['formal_decision']]
    assert acceptance_valid(record, found[0], source_row(rid))


def test_native_ids_are_unique_and_do_not_collide_with_either_prior_history():
    records = packet()['records']
    ids = {r['native_id'] for r in records}
    original = csv_records(published_bytes(BASE, DECISIONS))
    assert len(ids) == len(records) == 15
    assert ids.isdisjoint({r['decision_id'] for r in original})
    assert ids.isdisjoint(B4_01_RESERVED_IDS)


def test_all_original_decisions_remain_a_byte_identical_prefix():
    raw = (ROOT / DECISIONS).read_bytes()
    old = published_bytes(BASE, DECISIONS)
    assert sha(old) == packet()['source_sha256_before'][DECISIONS]
    assert raw.startswith(old)
    assert len(csv_records(old)) == packet()['prior_registry_rows'] == 103
    assert csv_records(raw)[:103] == csv_records(old)
    assert len(read_review_decisions()) == len({r['decision_id'] for r in read_review_decisions()})


@pytest.mark.parametrize('rid', ASSIGNED)
def test_native_repeat_submission_is_idempotent_without_rewriting_history(rid, tmp_path):
    target = tmp_path / 'review_decisions.csv'
    before = (ROOT / DECISIONS).read_bytes()
    target.write_bytes(before)
    decision = case(rid)['formal_decision']
    assert upsert_review_decision(decision, path=target) == decision
    assert upsert_review_decision(decision, path=target) == decision
    assert target.read_bytes() == before


@pytest.mark.parametrize('rid', ACCEPTED)
def test_only_three_authorized_venue_binding_cells_change_on_each_journal(rid):
    record, current = case(rid), source_row(rid)
    original = next(r for r in csv_records(published_bytes(BASE, PAPERS)) if r['paper_id'] == record['paper_id'])
    changes = record['binding']['accepted_venue_fields']
    assert current == {**original, **changes}
    expected_deltas = [{'paper_id':record['paper_id'], 'field':key, 'before':original[key], 'after':value}
                       for key, value in changes.items()]
    actual = [d for d in packet()['paper_cell_deltas'] if d['paper_id'] == record['paper_id']]
    assert sorted(actual, key=lambda d:d['field']) == sorted(expected_deltas, key=lambda d:d['field'])
    assert set(changes) == {'venue_id', 'venue_name', 'venue_type'}
    assert all(original[key] != current[key] for key in changes)


def test_transaction_delta_is_exactly_nine_cells_and_three_new_aliases():
    deltas = packet()['paper_cell_deltas']
    assert len(deltas) == 9
    assert {d['paper_id'] for d in deltas} == {case(rid)['paper_id'] for rid in ACCEPTED}
    appended = packet()['appended_venue_alias_rows']
    assert len(appended) == 3
    original = csv_records(published_bytes(BASE, ALIASES))
    assert sha(published_bytes(BASE, ALIASES)) == packet()['source_sha256_before'][ALIASES]
    current = read_rows(ALIASES)
    assert current[:len(original)] == original
    # Other independent batches may append their own entries; test this
    # transaction's unique entries without assuming global final row positions.
    for row in appended:
        assert current.count(row) == 1
        assert row['review_status'] == 'confirmed'
        assert row['venue_type'] == 'journal'
        assert row['venue_track'] == row['venue_acronym'] == ''
        assert row['venue_id'] in {case(rid)['binding']['accepted_venue_fields']['venue_id'] for rid in ACCEPTED}


@pytest.mark.parametrize('rid', ACCEPTED)
def test_journal_bindings_resolve_to_source_backed_registry_and_native_confirmation(rid):
    record = case(rid)
    aliases = read_venue_aliases()
    registry = canonical_venue_registry(aliases)
    source = source_row(rid)
    canonical = registry[source['venue_id']]
    assert all(canonical[k] == source[k] for k in ('venue_name', 'venue_type', 'venue_acronym'))
    assert source['venue'] == source['venue_name']
    audit = VenueAudit(aliases, evidence=[], decisions=[record['formal_decision']])
    assert confirmation_fingerprint(source) in audit.confirmations
    assert audit.paper(source)[1] is None


@pytest.mark.parametrize('rid,field,wrong', [
    (rid, field, wrong) for rid in ACCEPTED
    for field, wrong in [('doi', '10.9999/wrong-paper'), ('venue_name', 'Different Journal'), ('publication_type', 'conference')]
])
def test_identity_or_venue_change_invalidates_record_and_confirmation_fingerprint(rid, field, wrong):
    record = case(rid)
    changed = {**source_row(rid), field:wrong}
    assert confirmation_fingerprint(changed) != record['binding']['venue_state_fingerprint']
    audit = VenueAudit(read_venue_aliases(), evidence=[], decisions=[record['formal_decision']])
    assert confirmation_fingerprint(changed) not in audit.confirmations
    assert not acceptance_valid(record, record['formal_decision'], changed)


@pytest.mark.parametrize('fault', ['native_id', 'action', 'identity', 'binding_token', 'matrix_hash', 'venue_token', 'creator'])
def test_incomplete_or_mismatched_venue_acceptance_is_rejected(fault):
    record = deepcopy(case('P049'))
    decision = deepcopy(record['formal_decision'])
    if fault == 'native_id': decision['decision_id'] = 'review:' + '0' * 20
    elif fault == 'action': decision['action'] = 'unresolved'
    elif fault == 'identity': decision['title'] = 'Different Paper'
    elif fault == 'binding_token': decision['review_note'] = re.sub(r'\[b4-02-state:[a-f0-9]{64}\]', '', decision['review_note'])
    elif fault == 'matrix_hash': record['binding']['b3_matrix_sha256'] = '0' * 64
    elif fault == 'venue_token': decision['review_note'] = re.sub(r'\[venue-state:[a-f0-9]{64}\]', '', decision['review_note'])
    elif fault == 'creator': decision['created_by'] = 'automatic-unreviewed'
    assert not acceptance_valid(record, decision, source_row('P049'))


def test_p001_track_boundary_is_a_nonterminal_hold_without_silent_main_or_registry_addition():
    record, current = case('P001'), source_row('P001')
    original = next(r for r in csv_records(published_bytes(BASE, PAPERS)) if r['paper_id'] == record['paper_id'])
    assert current == original
    assert current['venue_track'] == current['venue_id'] == ''
    assert record['disposition'] == 'VENUE_BINDING_REQUIRES_TRACK_DECISION'
    assert record['formal_decision']['action'] == 'unresolved'
    assert record['binding']['accepted_venue_fields'] is None
    assert not any(a['venue_name'] == current['venue'] for a in packet()['appended_venue_alias_rows'])
    audit = VenueAudit(read_venue_aliases(), evidence=[], decisions=[record['formal_decision']])
    assert record['binding']['venue_state_fingerprint'] in audit.explicit_conflicts
    assert not audit.confirmations


def test_u005_keeps_precise_affiliation_distinct_from_unverified_viewport_and_author_presence():
    record = case('U005')
    policy = packet()['U005_precision_policy']['U005_precision_decision']
    assert record['formal_decision']['action'] == 'unresolved'
    assert record['disposition'] == 'LOCATION_PRECISION_NOT_REPRESENTABLE'
    assert policy['recommendation'] == 'RETAIN_UNRESOLVED'
    assert policy['accept_location_row'] is policy['accept_location_mapping_change'] is False
    point = policy['geographic_point']
    assert (point['latitude'], point['longitude']) == (47.789438, 22.876378)
    assert point['explicit_marker_verified'] is point['independent_geocode_verified'] is point['author_location_claim'] is False
    assert 'viewport' in point['point_kind']
    assert 'not' in policy['paper_time_author_location'].lower()
    assert {'coordinate_kind', 'coordinate_precision', 'crs', 'positional_uncertainty', 'marker_verified'}.isdisjoint(INSTITUTION_LOCATION_COLUMNS)
    assert '[venue-state:' not in record['formal_decision']['review_note']


def test_exact_u005_romania_draft_is_rejected_by_current_country_policy_without_saving():
    draft = {'institution_id':'institution:004b85aa254cbf69',
             'confirmed_institution':'Colegiul Național “Mihai Eminescu” Satu Mare',
             'confirmed_city':'Satu Mare', 'confirmed_region':'Satu Mare',
             'confirmed_country':'Romania', 'confirmed_country_code':'RO',
             'confirmed_lat':'47.789438', 'confirmed_lon':'22.876378'}
    with pytest.raises(CuratedLocationError, match='country_code must identify a supported ISO alpha-2 country'):
        _confirmed_location_fields(draft, created_by='test-only-no-save', normalized_institution=draft['confirmed_institution'])


def test_confirmation_cannot_represent_the_required_approximate_point_qualifiers():
    # This synthetic supported-country fixture is never a replacement U005
    # location; it isolates field semantics from Romania's separate blocker.
    draft = {'institution_id':'institution:synthetic-fixture', 'confirmed_institution':'Synthetic Fixture Institution',
             'confirmed_city':'Baltimore', 'confirmed_region':'Maryland', 'confirmed_country':'United States',
             'confirmed_country_code':'US', 'confirmed_lat':'39.29038', 'confirmed_lon':'-76.61219'}
    qualifiers = {'coordinate_kind':'official_embedded_map_viewport', 'coordinate_precision':'approximate',
                  'crs':'undeclared', 'positional_uncertainty':'unmeasured', 'marker_verified':False}
    converted = _confirmed_location_fields({**draft, **qualifiers, 'coordinate_status':'approximate'},
                                           created_by='test-only-no-save', normalized_institution=draft['confirmed_institution'])
    assert converted['coordinate_status'] == 'known'
    assert is_confirmed_location(converted)
    assert set(qualifiers).isdisjoint(converted)
    assert not is_confirmed_location({**converted, 'coordinate_status':'approximate'})


def test_location_mappings_and_institution_sources_have_no_data_change():
    for path in ('data/curated/institution_locations.csv', 'data/curated/author_institution_mappings.csv',
                 'data/curated/institutions.csv', 'data/curated/institution_aliases.csv',
                 'data/curated/institution_location_review.csv'):
        assert (ROOT / path).read_bytes() == published_bytes(BASE, path)
    assert not any(d['field'].startswith(('lat', 'lon', 'institution')) for d in packet()['paper_cell_deltas'])


def test_transaction_accounting_is_reconstructed_without_a_fixed_live_tail_position():
    original = csv_records(published_bytes(BASE, DECISIONS))
    transaction = [*original, *(r['formal_decision'] for r in packet()['records'])]
    assert len(original) == 103 and len(transaction) == 118
    closed = terminal(transaction)
    assert set(ASSIGNED) & closed.keys() == set(ACCEPTED)
    ledger = [r for r in decision_rows(load_queues()) if r['batch'] == 'B']
    pending = [r for r in ledger if r['review_id'] not in closed]
    active = [r for r in pending if r['paper_id'] in packet()['public_ids']]
    actual = {'original_actions':len(ledger), 'original_papers':len({r['paper_id'] for r in ledger}),
              'terminal_actions':len(closed), 'historical_unresolved_actions':len(pending),
              'historical_unresolved_papers':len({r['paper_id'] for r in pending}),
              'active_public_unresolved_actions':len(active), 'active_public_unresolved_papers':len({r['paper_id'] for r in active})}
    assert actual == packet()['accounting_after']
    assert actual['historical_unresolved_actions'] == 128
    assert actual['active_public_unresolved_actions'] == 126
    live_closed = terminal(read_review_decisions())
    assert set(ACCEPTED) <= live_closed.keys()
    assert set(HELD).isdisjoint(live_closed)


def test_public_identities_task_types_and_all_relationship_pairs_are_preserved():
    current, original = load_context(ROOT), published_context(BASE)
    assert set(current['papers']) == set(original['papers']) == set(packet()['public_ids'])
    assert current['counts'] == original['counts'] == packet()['corpus_unchanged']
    assert current['counts']['public'] == 674
    assert current['counts']['relationship_rows'] == current['counts']['unique_paper_institution_pairs'] == 1410
    assert current['pairs'] == original['pairs']
    for pid, paper in current['papers'].items():
        assert paper['tasks'] == original['papers'][pid]['tasks']
        assert paper['research_types'] == original['papers'][pid]['research_types']
    totals = dict(Counter(label for p in current['papers'].values() for label in p['tasks'] + p['research_types']))
    assert totals == packet()['taxonomy_unchanged']
    # Authoritative labels themselves, not only stale public JSON, stay fixed.
    assert (ROOT / 'data/curated/paper_taxonomy.csv').read_bytes() == published_bytes(BASE, 'data/curated/paper_taxonomy.csv')


def test_frozen_neurips_receipts_remain_exact_and_the_b3_correction_is_additive_only():
    frozen = packet()['frozen49_expected']
    assert len(frozen) == 49
    for path, digest in frozen.items():
        assert sha((ROOT / path).read_bytes()) == digest
    correction = packet()['additive_B3_correction']
    assert correction['review_id'] == 'U002'
    assert correction['SAMR_contact_postcode'] == '510630'
    assert correction['patent_CN112990582A_publication_2021_06_18_postcode'] == '510663'
    assert correction['B3_narrative_reversed_source_attribution'] is True
    assert correction['B3_matrix_correct'] is True
    assert correction['B3_modified'] is False
