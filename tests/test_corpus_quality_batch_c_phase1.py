"""Focused checks for the approved Batch C Phase 1, against committed Batch A."""
from collections import Counter
import csv
from functools import lru_cache
import hashlib
import io
import json
from pathlib import Path
import subprocess

import pytest

from scripts.validate_corpus_quality_audit import load_context, load_queues, decision_rows


ROOT = Path(__file__).resolve().parents[1]
BASE = '0bc98c3e75636899e53114be3d9de0a71986990c'
PHASE1 = 'ccb3fab'
LEDGER = ROOT / 'data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json'
PUBLIC = ('web/data/public_preview_papers.json', 'web/data/public_preview_map_data.json')
TARGETS = {
    'T363': ('curated:14272073fa5bc0e301b5', 'tasks', 'detection', 'detection;localization'),
    'R084': ('curated:980afddea0a156b5020b', 'research_types', 'method;dataset;benchmark', 'method'),
    'R121': ('curated:bada2e715200e9fccb7a', 'research_types', 'method;dataset;analysis_study', 'method;dataset'),
}


@lru_cache
def previous(path):
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT)


@lru_cache
def phase1(path):
    return subprocess.check_output(['git', 'show', PHASE1 + ':' + path], cwd=ROOT)


def csv_by_key(content, key):
    return {r[key]: r for r in csv.DictReader(io.StringIO(content.decode(), newline=''))}


@pytest.fixture(scope='module')
def state():
    return load_context(), json.loads(LEDGER.read_text())


@pytest.mark.parametrize('review_id', TARGETS)
def test_exact_approved_taxonomy_change(state, review_id):
    context, ledger = state
    pid, dimension, before, after = TARGETS[review_id]
    row = context['taxonomy'][pid]
    old = csv_by_key(previous('data/curated/paper_taxonomy.csv'), 'taxonomy_id')[row['taxonomy_id']]
    assert old[dimension] == before
    assert row[dimension] == after
    assert context['papers'][pid][dimension] == after.split(';')
    for companion in {'tasks', 'research_types', 'image_scopes'} - {dimension}:
        assert row[companion] == old[companion]
    disposition = next(d for d in ledger['resolved_dispositions'] if d['review_id'] == review_id)
    assert (disposition['before'], disposition['after']) == (before, after)


@pytest.mark.parametrize('path,key', [
    ('data/curated/paper_taxonomy.csv', 'taxonomy_id'),
    ('data/curated/papers.csv', 'paper_id'),
])
def test_only_three_authoritative_rows_and_approved_fields_change(state, path, key):
    context, _ = state
    old = csv_by_key(previous(path), key)
    new = csv_by_key((ROOT / path).read_bytes(), key)
    assert old.keys() == new.keys()
    allowed = {}
    for pid, dimension, _, _ in TARGETS.values():
        ident = context['taxonomy'][pid]['taxonomy_id'] if key == 'taxonomy_id' else pid
        allowed[ident] = {dimension}
        if key == 'taxonomy_id':
            allowed[ident] |= {dimension + '_review_reason', 'audited_at'}
    changed = {ident for ident in old if old[ident] != new[ident]}
    assert changed == allowed.keys()
    for ident in changed:
        fields = {f for f in old[ident] if old[ident][f] != new[ident][f]}
        assert fields == allowed[ident]


@pytest.mark.parametrize('path', PUBLIC)
def test_public_export_changes_are_confined_to_three_papers(state, path):
    context, _ = state
    old = json.loads(previous(path))
    # Keep this Phase 1 audit tied to the committed Phase 1 output. Later
    # adjudication waves may legitimately change active corpus membership.
    new = json.loads(phase1(path))
    assert old.keys() == new.keys()
    assert len(old['records']) == len(new['records'])
    for key in old.keys() - {'records', 'metadata'}:
        assert old[key] == new[key]
    # The existing exporter timestamps a real content change; all other metadata stays fixed.
    assert {k:v for k,v in old['metadata'].items() if k != 'public_preview_generated_at'} == {
        k:v for k,v in new['metadata'].items() if k != 'public_preview_generated_at'}
    allowed = {pid:dimension for pid,dimension,_,_ in TARGETS.values()}
    seen = set()
    for a, b in zip(old['records'], new['records']):
        if a == b:
            continue
        pid = b['paper_id']
        assert pid in allowed
        seen.add(pid)
        dimension = allowed[pid]
        assert {f for f in a.keys() | b.keys() if a.get(f) != b.get(f)} == {dimension, 'taxonomy_review'}
        assert b[dimension] == context['taxonomy'][pid][dimension].split(';')
        assert a['taxonomy_review'].keys() == b['taxonomy_review'].keys()
        for field in a['taxonomy_review'].keys() - {dimension}:
            assert a['taxonomy_review'][field] == b['taxonomy_review'][field]
    assert seen == allowed.keys()


def test_policy_lock_and_exact_reconciliation(state):
    _, ledger = state
    original = {r['review_id']: r for r in decision_rows(load_queues()) if r['batch'] == 'C'}
    resolved = ledger['resolved_dispositions']
    residual = ledger['residual_triage']
    assert ledger['baseline_commit'] == BASE
    assert {r['review_id'] for r in resolved} == {'T363', 'R084', 'R121', 'L001', 'P222'}
    assert len(resolved) == 5 and sum(r['authoritative_data_changed'] for r in resolved) == 3
    all_ids = [r['review_id'] for r in resolved + residual]
    assert len(all_ids) == len(set(all_ids)) == len(original)
    assert set(all_ids) == original.keys()
    policies = {p['policy_id']:p for p in ledger['policies']}
    assert len(ledger['policies']) == len(policies) == 12
    assert set(policies) == {'T1','T2','T3','R1','R2','R3','R4','I1','I2','P1','V1','V3'}
    assert Counter(p['decision'] for p in policies.values()) == {'ACCEPT':11, 'MODIFY_AND_ACCEPT':1}
    assert policies['T3']['decision'] == 'MODIFY_AND_ACCEPT'
    assert policies['T3']['final_rule'] == (
        'Every public paper must remain connected to at least one core forensic task represented by the map: '
        'detection, source_attribution, or localization. If careful review establishes that none applies, '
        'the record requires scope review rather than an empty task set.')
    owned = [rid for p in policies.values() for rid in p['affected_review_ids']]
    assert len(owned) == len(set(owned)) and set(owned) == original.keys() - {'R188'}
    for p in policies.values():
        assert p['date'] == '2026-10-05' and p['final_rule']
        assert set(p['policy_alone_resolves']) == set(p['affected_review_ids'])
    assert not policies['T3']['policy_alone_resolves']['T527']
    actual_batches = Counter(r['batch'] for r in decision_rows(load_queues()))
    reconciliation = ledger['reconciliation']
    assert reconciliation['original_batch_counts'] == dict(actual_batches)
    assert reconciliation['remaining_batch_c'] == actual_batches['C'] - len(resolved) == len(residual)
    assert reconciliation['batch_b_remaining'] == actual_batches['B'] == 159
    assert reconciliation['batch_d_remaining'] == actual_batches['D'] == 1752


def test_residual_triage_has_evidence_and_no_applied_proposals(state):
    _, ledger = state
    statuses = {'LOCAL_EVIDENCE_SUFFICIENT','EXTERNAL_PRIMARY_SOURCE_REQUIRED','MAINTAINER_SCOPE_JUDGMENT_REQUIRED'}
    counts = Counter()
    for row in ledger['residual_triage']:
        status = row['evidence_status']
        assert status in statuses
        counts[status] += 1
        assert row['applied'] is False and row['local_finding'] and row['evidence']
        for source in row['evidence']:
            path = source['path']
            assert (ROOT / path).is_file() and source['locator']
            assert hashlib.sha256(previous(path)).hexdigest() == source['sha256_at_review']
        if status == 'LOCAL_EVIDENCE_SUFFICIENT':
            assert row['proposed_factual_disposition']
        elif status == 'EXTERNAL_PRIMARY_SOURCE_REQUIRED':
            assert row['missing_external_evidence'] and row['proposed_factual_disposition'] is None
        else:
            assert row['maintainer_question'] and row['review_id'] == 'T527'
    assert ledger['reconciliation']['triage_counts'] == {s:counts[s] for s in statuses}


def test_t527_unchanged_and_no_new_empty_task_set(state):
    context, ledger = state
    pid = 'doi:10.1109/lsp.2024.3388958'
    current = context['taxonomy'][pid]
    old_registry = csv_by_key(previous('data/curated/paper_taxonomy.csv'), 'taxonomy_id')
    assert current == old_registry[current['taxonomy_id']]
    assert current['tasks'] == 'source_attribution'
    row = next(r for r in ledger['residual_triage'] if r['review_id'] == 'T527')
    assert row['review_state'] == 'SCOPE_OR_TASK_EVIDENCE_REQUIRED'
    before = json.loads(previous(PUBLIC[0]))['records']
    after = list(context['papers'].values())
    assert {r['title'] for r in before if not r['tasks']} == {r['title'] for r in after if not r['tasks']}
    assert {r['title'] for r in ledger['t3_existing_empty_core_tasks']['records']} == {r['title'] for r in after if not r['tasks']}


def test_p222_canonical_identity_and_complete_noop(state):
    context, ledger = state
    pid = 'curated:e9594b5466110ca009aa'
    paper = context['papers'][pid]
    assert paper['venue_name'] == paper['venue'] == 'IEEE MultiMedia'
    assert paper['venue_id'] == 'venue:ieee-multimedia' and not paper.get('venue_acronym')
    assert paper['publication_type'] == 'journal'
    assert paper == next(p for p in json.loads(previous(PUBLIC[0]))['records'] if p.get('paper_id') == pid)
    row = next(r for r in ledger['resolved_dispositions'] if r['review_id'] == 'P222')
    assert row['outcome'] == 'ALREADY_COMPLIANT_NO_DATA_CHANGE' and not row['authoritative_data_changed']


def test_ucsb_provenance_and_public_relationships_are_unchanged(state):
    _, ledger = state
    for path in PUBLIC:
        select = lambda payload: [r for r in payload['records'] if r.get('arxiv_id') == '2007.10466']
        old = select(json.loads(previous(path)))
        new = select(json.loads((ROOT / path).read_text()))
        assert old == new
        if 'map_data' in path:
            assert sum(r['institution_id'] == 'institution:de4a2849d3de43a3' for r in new) == 1
    for path in ('data/curated/author_institution_mappings.csv',
                 'data/curated/institution_author_overrides.csv',
                 'data/raw/corpus_quality_audit_2026_10_04/relationship_review.json',
                 'data/raw/corpus_quality_batch_a_2026_10_04/results.json'):
        assert (ROOT / path).read_bytes() == previous(path)
    history = json.loads((ROOT / 'data/raw/corpus_quality_audit_2026_10_04/relationship_review.json').read_text())
    sources = next(r for r in history['records'] if r['review_id'] == 'L001')['rows']
    assert {r['openalex_url'] for r in sources} == {'https://openalex.org/W3179128750','https://openalex.org/W3043994911'}
    protected = ledger['protected_state']
    assert protected['UCSB_R3'] == 'R3_RESOLVED_BY_PROVENANCE_POLICY'
    assert protected['UCSB_export'] == 'DETERMINISTIC_EXPORT_COLLAPSE_AFTER_R1_R2'
    assert protected['UCSB_manual_merge'] == 'NO MANUAL R3 MERGE APPLIED'


def test_recomputed_counts_and_registry_export_synchronization(state):
    context, ledger = state
    assert ledger['corpus_after'] == ledger['corpus_before']
    assert ledger['corpus_after'] == dict(public=640, formal=532, mapped=617, unmapped=23,
                                         relationship_rows=1422,
                                         unique_paper_institution_pairs=1422)
    # Wave 1 later excludes the text-only R188 record at the publication gate.
    assert context['counts'] == dict(public=639, formal=531, mapped=616, unmapped=23,
                                    relationship_rows=1419,
                                    unique_paper_institution_pairs=1419)
    for dimension in ('tasks','research_types'):
        registry_totals = Counter(label for row in context['taxonomy'].values() for label in row[dimension].split(';') if label)
        expected_current = Counter(ledger['taxonomy_after'][dimension])
        expected_current.subtract({'detection': 1} if dimension == 'tasks' else {'method': 1})
        assert registry_totals == +expected_current
        old = Counter(label for row in json.loads(previous(PUBLIC[0]))['records'] for label in row[dimension])
        phase1_totals = Counter(label for row in json.loads(phase1(PUBLIC[0]))['records'] for label in row[dimension])
        assert dict(old) == ledger['taxonomy_before'][dimension]
        expected = old.copy()
        for _, dim, before, after in TARGETS.values():
            if dim == dimension:
                expected.subtract(before.split(';'))
                expected.update(after.split(';'))
        assert phase1_totals == expected
        for pid, paper in context['papers'].items():
            assert paper[dimension] == [v for v in context['taxonomy'][pid][dimension].split(';') if v]


def test_original_decision_sheet_is_preserved_as_history(state):
    _, ledger = state
    sheet = (ROOT / 'docs/corpus_quality_batch_c_decision_sheet_2026_10_05.md').read_bytes()
    protected = ledger['protected_state']
    original = sheet[:protected['original_decision_sheet_bytes']]
    assert hashlib.sha256(original).hexdigest() == protected['original_decision_sheet_sha256']
    assert b'## D. Maintainer decisions' in sheet[len(original):]
