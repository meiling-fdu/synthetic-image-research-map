"""Live B5-01 integration: both immutable B4 histories and exact public effects.

These current-state guards complement the historical B1 transaction receipts.
No exporter, network request, repository write or HTTP fixture is invoked.
"""
from collections import Counter
from copy import deepcopy
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re

from scripts.curated_export import PaperIdentityCache, PaperIdentityIndex
from scripts.paper_links import resolve_public_links
from scripts.validate_corpus_quality_audit import decision_rows, load_context, load_queues
from tests.corpus_quality_test_helpers import csv_records, published_bytes, published_context

ROOT = Path(__file__).resolve().parents[1]
BASE = '7fc8ceae702324628335944cf4b545a3733fdc56'
MANIFEST = 'data/raw/corpus_quality_batch_b_wave_b5_01_2026_10_30/integration_manifest.json'
PAPERS = 'data/curated/papers.csv'
OVERRIDES = 'data/curated/publication_overrides.csv'
ALIASES = 'data/curated/venue_aliases.csv'
DECISIONS = 'data/curated/review_decisions.csv'
PUBLIC = ('web/data/public_preview_papers.json', 'web/data/public_preview_map_data.json')
GENERATED_MAPPING_REPORT = 'data/manual/missing_author_mappings_report.csv'
URL_ACTIONS = ['P034', 'P254', 'P305', 'P097', 'P105', 'P150', 'P177', 'P229']
VENUE_ACTIONS = ['P049', 'P058', 'P068']
HELD = ['P028', 'P001', 'U001', 'U002', 'U003', 'U005', 'U006', 'U007',
        'U008', 'U014', 'U016', 'U018', 'U023']
NATIVE_FIELDS = ('review_queue', 'target_type', 'doi', 'openalex_url', 'title', 'year', 'institution')
URL_PUBLIC_FIELDS = {'paper_url', 'url', 'formal_url', 'primary_url', 'landing_page_url', 'is_arxiv_preprint', 'notes'}
VENUE_PUBLIC_FIELDS = {'venue_id', 'venue_name', 'venue_type', 'venue_acronym', 'venue_track',
                       'venue_label', 'venue_aliases', 'venue_review_required', 'venue_review_reason',
                       'ambiguity_status', 'raw_venue', 'metadata_status'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


@lru_cache
def packet():
    return json.loads((ROOT / MANIFEST).read_text())


def actual_rows(path):
    return csv_records((ROOT / path).read_bytes())


@lru_cache
def transactions():
    loaded = []
    for item in packet()['transactions']:
        raw = (ROOT / item['manifest_path']).read_bytes()
        assert sha(raw) == item['manifest_sha256']
        loaded.append(json.loads(raw))
    assert len(loaded) == 2
    return loaded


@lru_cache
def cases():
    result = {}
    for tx in transactions():
        for row in tx['records']:
            assert row['review_id'] not in result
            result[row['review_id']] = row
    return result


def native_id(decision):
    identity = '|'.join(' '.join(str(decision.get(k, '')).split()).casefold() for k in NATIVE_FIELDS)
    return 'review:' + sha(identity.encode())[:20]


def terminal(rows):
    result = {}
    special = {'review:b9f458d69de24b8aae0a':'R267', 'review:aa32e93a24ade10ed99d':'R236'}
    for row in rows:
        if row['action'] != 'no_action_after_review':
            continue
        match = re.search(r'\bBatch B review ([A-Z]\d{3});', row['review_note'])
        rid = match[1] if match else special.get(row['decision_id'])
        if rid:
            assert rid not in result, 'Duplicate terminal decision for one original review action'
            result[rid] = row
    return result


def accounting(rows, public_ids):
    ledger = [r for r in decision_rows(load_queues()) if r['batch'] == 'B']
    closed = terminal(rows)
    pending = [r for r in ledger if r['review_id'] not in closed]
    active = [r for r in pending if r['paper_id'] in public_ids]
    return {'original_actions':len(ledger), 'original_papers':len({r['paper_id'] for r in ledger}),
            'terminal_actions':len(closed), 'historical_unresolved_actions':len(pending),
            'historical_unresolved_papers':len({r['paper_id'] for r in pending}),
            'active_public_unresolved_actions':len(active), 'active_public_unresolved_papers':len({r['paper_id'] for r in active})}


def changed_fields(before, after):
    return {key for key in before.keys() | after.keys() if before.get(key) != after.get(key)
            or (key in before) != (key in after)}


@lru_cache
def live_context():
    return load_context(ROOT)


@lru_cache
def public_maps():
    return {r['id']:r for r in json.loads((ROOT / PUBLIC[1]).read_bytes())['records']}


@lru_cache
def previous_maps():
    return {r['id']:r for r in json.loads(published_bytes(BASE, PUBLIC[1]))['records']}


@lru_cache
def map_paper_ids():
    # Do not require legacy public rows to carry paper_id. Resolve through the
    # same authoritative taxonomy identities used by the published endpoints.
    index = PaperIdentityIndex(actual_rows('data/curated/paper_taxonomy.csv'), PaperIdentityCache())
    canonical = published_context(BASE)['taxonomy_to_public_id']
    result = {}
    for mid, row in public_maps().items():
        found = index.matches(row)
        assert len(found) == 1
        result[mid] = canonical[found[0]['taxonomy_id']]
    return result


def test_integration_reuses_two_exact_immutable_adjudications_without_identifier_remapping():
    assert packet()['baseline_commit'] == BASE
    assert set(cases()) == set(URL_ACTIONS + VENUE_ACTIONS + HELD)
    assert len(cases()) == 24
    assert packet()['accepted_review_ids'] == URL_ACTIONS + VENUE_ACTIONS
    assert packet()['held_review_ids'] == HELD
    assert [r['review_id'] for r in cases().values() if r['accepted']] == URL_ACTIONS + VENUE_ACTIONS
    assert [r['review_id'] for r in cases().values() if not r['accepted']] == HELD
    for row in cases().values():
        assert row['native_id'] == row['formal_decision']['decision_id'] == native_id(row['formal_decision'])
        assert row['binding']['review_id'] == row['review_id']
        assert row['binding']['baseline_commit'] == BASE


def test_all_127_formal_rows_preserve_the_original_103_bytes_and_both_append_histories():
    baseline = published_bytes(BASE, DECISIONS)
    current = (ROOT / DECISIONS).read_bytes()
    before, after = csv_records(baseline), csv_records(current)
    assert len(before) == 103 and len(after) == 127
    assert current.startswith(baseline) and after[:103] == before
    expected = [r['formal_decision'] for tx in transactions() for r in tx['records']]
    assert after[103:] == expected and len(expected) == 24
    assert len({r['decision_id'] for r in after}) == len(after)
    assert packet()['decision_ids'] == [r['decision_id'] for r in expected]
    # Preserve the original B4-01[:112] transaction boundary; B4-02 tests locate
    # their live rows by ID and reconstruct their independent endpoint.
    assert after[103:112] == [r['formal_decision'] for r in transactions()[0]['records']]


def test_action_ids_and_per_action_transaction_fingerprints_are_collision_free():
    rows = list(cases().values())
    assert len({r['native_id'] for r in rows}) == 24
    assert len({r['binding_sha256'] for r in rows}) == 24
    for row in rows:
        digest = sha(json.dumps(row['binding'], sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())
        assert digest == row['binding_sha256']
        assert digest in row['formal_decision']['review_note']
    # Shared evidence/matrix hashes are intentionally not unique-action keys.
    assert {r['review_id'] for r in rows} == set(URL_ACTIONS + VENUE_ACTIONS + HELD)


def test_only_eleven_actions_close_and_all_thirteen_new_holds_remain_open():
    old = terminal(csv_records(published_bytes(BASE, DECISIONS)))
    now = terminal(actual_rows(DECISIONS))
    assert set(now) - set(old) == set(URL_ACTIONS + VENUE_ACTIONS)
    assert set(HELD).isdisjoint(now)
    for rid, row in cases().items():
        assert row['formal_decision']['action'] == ('no_action_after_review' if rid in URL_ACTIONS + VENUE_ACTIONS else 'unresolved')
        assert row['formal_decision']['review_note'].startswith('Batch B review ' + rid + ';')


def test_unresolved_accounting_is_derived_from_the_live_original_ledger_and_public_identities():
    public = live_context()['papers']
    old = accounting(csv_records(published_bytes(BASE, DECISIONS)), public)
    now = accounting(actual_rows(DECISIONS), public)
    assert old == packet()['accounting_before']
    assert now == packet()['accounting_after']
    assert old['historical_unresolved_actions'] - now['historical_unresolved_actions'] == 11
    assert old['active_public_unresolved_actions'] - now['active_public_unresolved_actions'] == 11
    assert (now['historical_unresolved_actions'], now['active_public_unresolved_actions']) == (120,118)
    assert (now['historical_unresolved_papers'], now['active_public_unresolved_papers']) == (113,111)


def test_exact_fifteen_paper_cells_change_without_identity_authors_dates_or_taxonomy_edits():
    old, new = csv_records(published_bytes(BASE, PAPERS)), actual_rows(PAPERS)
    assert [r['paper_id'] for r in old] == [r['paper_id'] for r in new]
    deltas = [{'paper_id':a['paper_id'], 'field':key, 'before':a[key], 'after':b[key]}
              for a,b in zip(old,new) for key in a if a[key] != b[key]]
    normalize = lambda values: sorted(values,key=lambda r:(r['paper_id'],r['field']))
    assert normalize(deltas) == normalize(packet()['paper_cell_deltas'])
    assert len(deltas) == 15
    assert Counter(d['field'] for d in deltas) == {'paper_url':6,'venue_id':3,'venue_name':3,'venue_type':3}
    expected = [*transactions()[0]['paper_url_cell_deltas'], *transactions()[1]['paper_cell_deltas']]
    assert normalize(deltas) == normalize(expected)
    assert {d['paper_id'] for d in deltas if d['field']=='paper_url'}.isdisjoint(
        {d['paper_id'] for d in deltas if d['field'].startswith('venue_')})


def test_url_override_and_alias_appends_are_exact_without_changing_prior_rows():
    for path,key,expected_count in [(OVERRIDES,'appended_publication_override_rows',2),(ALIASES,'appended_venue_alias_rows',3)]:
        before_raw, after_raw = published_bytes(BASE,path), (ROOT/path).read_bytes()
        before, after = csv_records(before_raw), csv_records(after_raw)
        assert after_raw.startswith(before_raw)
        assert after[:len(before)] == before
        expected = [{k:str(v) for k,v in row.items()} for row in packet()[key]]
        assert after[len(before):] == expected
        assert len(after)-len(before) == expected_count
    csv_values = lambda rows: [{k:str(v) for k,v in row.items()} for row in rows]
    assert csv_values(packet()['appended_publication_override_rows']) == csv_values(transactions()[0]['appended_publication_overrides'])
    assert packet()['appended_venue_alias_rows'] == transactions()[1]['appended_venue_alias_rows']


def test_only_four_authoritative_csv_files_have_changed_and_their_fingerprints_match():
    allowed = {PAPERS,OVERRIDES,ALIASES,DECISIONS}
    for path,digest in packet()['source_before_sha256'].items():
        assert sha(published_bytes(BASE,path)) == digest
    for path,digest in packet()['source_after_sha256'].items():
        assert sha((ROOT/path).read_bytes()) == digest
    # A complete current-state byte guard complements the historical B1 tests.
    import subprocess
    paths = subprocess.check_output(['git','--no-optional-locks','ls-tree','-r','--name-only',BASE,'--','data/curated','data/manual'],cwd=ROOT,text=True).splitlines()
    for path in paths:
        # This is an explicitly generated URL report, not a manual override.
        # Its exact eight URL-cell changes are independently checked below.
        if path not in allowed | {GENERATED_MAPPING_REPORT}:
            assert (ROOT/path).read_bytes() == published_bytes(BASE,path), path


def test_all_eight_live_publication_urls_match_the_authorized_paper_identities():
    public = live_context()['papers']
    for rid in URL_ACTIONS:
        record = cases()[rid]
        paper = public[record['paper_id']]
        accepted = record['binding']['accepted_url']
        assert paper['title'] == record['title']
        assert paper['formal_url'] == resolve_public_links(paper)['formal_url'] == accepted
        assert paper['doi'] == published_context(BASE)['papers'][record['paper_id']]['doi']
        assert paper['authors'] == published_context(BASE)['papers'][record['paper_id']]['authors']


def test_all_three_live_journal_bindings_match_their_accepted_registry_states():
    from scripts.venues import canonical_venue_registry,read_venue_aliases
    registry = canonical_venue_registry(read_venue_aliases())
    for rid in VENUE_ACTIONS:
        record = cases()[rid]
        paper = live_context()['papers'][record['paper_id']]
        for field,value in record['binding']['accepted_venue_fields'].items():
            assert paper[field] == value
        assert paper['publication_type'] == paper['venue_type'] == 'journal'
        assert paper['venue'] == paper['venue_name'] == registry[paper['venue_id']]['venue_name']
        assert paper.get('venue_acronym','') == paper.get('venue_track','') == ''
        assert paper['authors'] == published_context(BASE)['papers'][record['paper_id']]['authors']


def test_live_publication_changes_are_limited_to_eleven_accepted_papers_and_optional_p001_reason():
    old,new = published_context(BASE)['papers'],live_context()['papers']
    assert old.keys() == new.keys()
    actual = {pid:changed_fields(old[pid],new[pid]) for pid in old if old[pid] != new[pid]}
    accepted = {cases()[rid]['paper_id'] for rid in URL_ACTIONS+VENUE_ACTIONS}
    p001 = cases()['P001']['paper_id']
    assert set(actual) in (accepted,accepted|{p001})
    assert set(actual) == set(packet()['export_audit']['changed_paper_ids'])
    assert {pid:set(fields) for pid,fields in packet()['export_audit']['fields_by_paper'].items()} == actual
    for rid in URL_ACTIONS:
        assert actual[cases()[rid]['paper_id']] <= URL_PUBLIC_FIELDS
    for rid in VENUE_ACTIONS:
        assert actual[cases()[rid]['paper_id']] <= VENUE_PUBLIC_FIELDS
    if p001 in actual:
        assert actual[p001] == {'venue_review_reason'}
        assert new[p001]['venue_review_required'] is True
        assert new[p001]['ambiguity_status'] == 'unresolved'


def test_all_public_bibliographic_identities_and_task_type_labels_are_unchanged():
    old,new = published_context(BASE)['papers'],live_context()['papers']
    for pid in old:
        for field in ('title','year','authors','doi','arxiv_id','publication_type','tasks','image_scopes','research_types'):
            assert new[pid].get(field) == old[pid].get(field), (pid,field)
    assert (ROOT/'data/curated/paper_taxonomy.csv').read_bytes() == published_bytes(BASE,'data/curated/paper_taxonomy.csv')


def test_all_relationship_identities_pairs_affiliations_and_coordinates_are_preserved():
    old,new = previous_maps(),public_maps()
    assert old.keys() == new.keys()
    assert len(new) == 1410
    assert live_context()['pairs'] == published_context(BASE)['pairs']
    for mid in old:
        for field in ('id','institution_id','institution','authors','affiliations','lat','lon','latitude','longitude',
                      'country','country_code','city','region','tasks','image_scopes','research_types'):
            assert new[mid].get(field) == old[mid].get(field), (mid,field)


def test_all_changed_map_rows_are_exact_url_dependents_with_correct_semantic_links():
    old,new = previous_maps(),public_maps()
    actual = {mid:changed_fields(old[mid],new[mid]) for mid in old if old[mid]!=new[mid]}
    assert set(actual) == set(packet()['export_audit']['changed_map_ids'])
    assert {mid:set(fields) for mid,fields in packet()['export_audit']['fields_by_map'].items()} == actual
    expected_papers = {cases()[rid]['paper_id'] for rid in URL_ACTIONS}
    expected = {mid for mid,pid in map_paper_ids().items() if pid in expected_papers}
    assert set(actual) == expected
    assert len(actual) == 23
    by_paper = {cases()[rid]['paper_id']:cases()[rid]['binding']['accepted_url'] for rid in URL_ACTIONS}
    for mid,fields in actual.items():
        assert fields <= URL_PUBLIC_FIELDS
        assert new[mid]['formal_url'] == by_paper[map_paper_ids()[mid]]
        assert resolve_public_links(new[mid])['formal_url'] == new[mid]['formal_url']


def test_all_unresolved_p001_and_u005_policy_boundaries_survive_publication():
    source = {p['paper_id']:p for p in actual_rows(PAPERS)}
    p001 = cases()['P001']
    row = source[p001['paper_id']]
    old = next(p for p in csv_records(published_bytes(BASE,PAPERS)) if p['paper_id']==p001['paper_id'])
    assert row == old and row['venue_track'] == row['venue_id'] == ''
    assert cases()['U005']['disposition'] == 'LOCATION_PRECISION_NOT_REPRESENTABLE'
    assert p001['disposition'] == 'VENUE_BINDING_REQUIRES_TRACK_DECISION'
    for rid in HELD:
        assert cases()[rid]['formal_decision']['action'] == 'unresolved'
    for path in ('data/curated/institution_locations.csv','data/curated/author_institution_mappings.csv',
                 'data/curated/institution_location_review.csv'):
        assert (ROOT/path).read_bytes() == published_bytes(BASE,path)


def test_corpus_and_taxonomy_totals_are_recomputed_and_match_source_and_public_invariants():
    context = live_context()
    assert context['counts'] == packet()['corpus_counts']
    assert context['counts'] == {'public':674,'formal':557,'mapped':613,'unmapped':61,
                                 'relationship_rows':1410,'unique_paper_institution_pairs':1410}
    public = Counter(label for p in context['papers'].values() for label in p['tasks']+p['research_types'])
    source = Counter(label for r in context['taxonomy'].values() for dim in ('tasks','research_types') for label in r[dim].split(';') if label)
    assert public == source == packet()['taxonomy']
    assert public == {'detection':621,'source_attribution':84,'localization':45,'method':578,
                      'dataset':138,'benchmark':97,'survey':21,'analysis_study':86}


def test_current_paired_export_metadata_has_one_valid_utc_generation_timestamp():
    from scripts.public_export_metadata import is_utc_timestamp
    times = []
    for path in PUBLIC:
        old,new = json.loads(published_bytes(BASE,path)),json.loads((ROOT/path).read_bytes())
        before,after = dict(old['metadata']),dict(new['metadata'])
        oldtime = before.pop('public_preview_generated_at')
        newtime = after.pop('public_preview_generated_at')
        assert before == after
        assert newtime >= oldtime and is_utc_timestamp(newtime)
        assert {k:v for k,v in old.items() if k not in {'records','metadata'}} == {k:v for k,v in new.items() if k not in {'records','metadata'}}
        times.append(newtime)
    assert len(set(times)) == 1


def test_original_reports_and_manifests_still_expose_all_evidence_caveats():
    p034 = cases()['P034']
    original = p034['b3_evidence_record']['reviewer_evidence_record']['identity_evidence']
    assert (original['canonical_author_count'],original['publisher_author_count']) == (12,13)
    assert 'Manni Cui' in original['author_difference']
    b402 = transactions()[1]
    correction = b402['additive_B3_correction']
    assert correction['SAMR_contact_postcode'] == '510630'
    assert correction['patent_CN112990582A_publication_2021_06_18_postcode'] == '510663'
    assert correction['B3_modified'] is False
    policy = b402['U005_precision_policy']['U005_precision_decision']
    assert not policy['accept_location_row'] and not policy['accept_location_mapping_change']


def test_generated_mapping_report_changes_only_eight_authorized_url_cells():
    old = csv_records(published_bytes(BASE, GENERATED_MAPPING_REPORT))
    new = actual_rows(GENERATED_MAPPING_REPORT)
    assert len(old) == len(new) == len(live_context()['papers']) == 674
    assert [r['paper_id'] for r in old] == [r['paper_id'] for r in new]
    index = PaperIdentityIndex(actual_rows('data/curated/paper_taxonomy.csv'), PaperIdentityCache())
    canonical = published_context(BASE)['taxonomy_to_public_id']
    expected = {cases()[rid]['paper_id']:cases()[rid]['binding']['accepted_url'] for rid in URL_ACTIONS}
    changed = {}
    for before, after in zip(old, new):
        if before == after:
            continue
        assert changed_fields(before, after) == {'url'}
        found = index.matches(before)
        assert len(found) == 1
        pid = canonical[found[0]['taxonomy_id']]
        assert pid not in changed and pid in expected
        assert after['url'] == expected[pid]
        changed[pid] = after['url']
    assert changed == expected


def test_three_journal_metadata_status_changes_do_not_accept_unresolved_affiliations():
    old, new = published_context(BASE)['papers'], live_context()['papers']
    selected = {cases()[rid]['paper_id'] for rid in VENUE_ACTIONS}
    for pid, before in old.items():
        after = new[pid]
        if pid not in selected:
            assert after.get('metadata_status') == before.get('metadata_status')
            continue
        assert before['venue_review_required'] is True
        assert after['venue_review_required'] is False
        assert after['needs_review'] == before['needs_review'] is True
        assert after['missing_coordinates'] == before['missing_coordinates'] is True
        expected = deepcopy(before['metadata_status'])
        assert expected['field_overrides']['venue']['status'] == 'Needs review'
        expected['field_overrides'].pop('venue')
        # Clearing the venue flag exposes the existing affiliation review debt;
        # it must not create a new accepted affiliation or geographic claim.
        expected['field_overrides']['affiliations'] = {'status':'Needs review'}
        assert after['metadata_status'] == expected
