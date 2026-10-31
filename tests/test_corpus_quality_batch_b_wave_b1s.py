"""B1S synchronizes only accepted R026/R253 contributions and preserves scientific limits.

Current source, registry and public-output gates are independent of frozen B1P
transaction receipts. No pipeline invocation, network or repository mutation.
"""
from collections import Counter
from copy import deepcopy
import csv
from datetime import datetime
from functools import lru_cache
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

import pytest

from scripts.curated_schema import (
    ALLOWED_REVIEW_ACTIONS, ALLOWED_REVIEW_QUEUES, PAPERS_COLUMNS,
    PAPER_TAXONOMY_COLUMNS, REVIEW_DECISION_COLUMNS,
)
from scripts.paper_taxonomy_registry import read_paper_taxonomy_registry, public_taxonomy_fields
from scripts.review_decisions import read_review_decisions, upsert_review_decision
from scripts.validate_corpus_quality_audit import decision_rows, load_context, load_queues
from scripts.literature51_reproducibility import preserved_bytes
from tests.test_corpus_quality_batch_b_wave_b1n import logical_csv_chunks, replace_csv_tokens
from tests.corpus_quality_test_helpers import published_context
from tests.baseline_expectations import CURRENT_CORPUS_COUNTS, CURRENT_TAXONOMY_TOTALS

ROOT = Path(__file__).resolve().parents[1]
BASELINE = {'baseline': 'dace181c2a9edbb7c467978e9e958e83fdddc143',
 'evidence_sha256': {'data/raw/corpus_quality_batch_b_wave_b1q_2026_10_26/evidence_manifest.json': '07deb03f59a03015bb4e8b055b23e1a0f2e9ece66eba750b7354356d37981002',
                     'docs/corpus_quality_batch_b_wave_b1q_2026_10_26.md': 'bccebf430c6d39b815ae63bed40844fdc92b658bf8078e61a65ccddc174c3686'}}
FROZEN = {'baseline_commit': 'dace181c2a9edbb7c467978e9e958e83fdddc143',
 'pre_export_frozen_source_sha256': {'data/raw/corpus_quality_batch_b_wave_b1q_2026_10_26/evidence_manifest.json': '07deb03f59a03015bb4e8b055b23e1a0f2e9ece66eba750b7354356d37981002',
                                     'docs/corpus_quality_batch_b_wave_b1q_2026_10_26.md': 'bccebf430c6d39b815ae63bed40844fdc92b658bf8078e61a65ccddc174c3686',
                                     'docs/corpus_quality_batch_b_wave_b1r_2026_10_27.md': '2606eb4933540741e96c733ff8275d104b1c63efb15194abda27f54592e30e25',
                                     'data/curated/paper_taxonomy.csv': '2388617d62211ebea18af8827095a1a776ce0c160d1942511212fa7324fe0fb9',
                                     'data/curated/papers.csv': '8ff6f43f054b6da18ef498cc7c0b9d4fcf7bd6cc9a9abd01d67255b1909bc65f',
                                     'data/curated/review_decisions.csv': 'ce616e76f5b41a2df967c9c72451f9cbeb8b1ad05b488d5ca6240d070c4819dc'}}
BASE = BASELINE['baseline']
# Exact B1S transaction receipts end at its immutable publication. Later
# approved venue/URL changes are checked by B5's live integration guards.
PUBLISHED = 'df9774b64f717d535d3f299a727545f4b9488adb'
PAPERS = 'data/curated/papers.csv'
TAXONOMY = 'data/curated/paper_taxonomy.csv'
DECISIONS = 'data/curated/review_decisions.csv'
PUBLIC = ('web/data/public_preview_papers.json', 'web/data/public_preview_map_data.json')
TARGETS = {'R026': 'curated:386ccd052b812587c286', 'R253': 'curated:f9eac1aa13a606c6ec88'}
TYPES = {'R026': ['method', 'analysis_study'], 'R253': ['method', 'dataset', 'benchmark']}
IDS = {'R026': 'review:001acb4497ed65ffc78b', 'R253': 'review:be6652347897359ff3b3'}
POLICIES = {'R026': 'R3', 'R253': 'R2'}
ALLOW = {
    PAPERS: {'research_types'},
    TAXONOMY: {'research_types', 'research_types_review_reason', 'research_types_evidence_tier',
               'research_types_evidence_source', 'research_types_evidence_excerpt', 'audited_at'},
}
IDENTITY = ('review_queue', 'target_type', 'doi', 'openalex_url', 'title', 'year', 'institution')
B1O_TERMINAL = {'R267': 'review:b9f458d69de24b8aae0a', 'R236': 'review:aa32e93a24ade10ed99d'}
MANIFEST = next(p for p in BASELINE['evidence_sha256'] if p.endswith('.json'))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


@lru_cache
def baseline(path):
    return subprocess.check_output(['git', '--no-optional-locks', 'show', f'{BASE}:{path}'], cwd=ROOT)


@lru_cache
def endpoint_bytes(path):
    return subprocess.check_output(['git', '--no-optional-locks', 'show', f'{PUBLISHED}:{path}'], cwd=ROOT)


def csv_rows(raw):
    return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'), newline='')))


def row_by_pid(rows, pid):
    matched = [row for row in rows if row['paper_id'] == pid]
    assert len(matched) == 1
    return matched[0]


@lru_cache
def packet():
    return json.loads((ROOT / MANIFEST).read_bytes())


def source_record(rid):
    matches = [row for row in packet()['records'] if row['review_id'] == rid]
    assert len(matches) == 1
    return matches[0]


def decision_id(row):
    identity = '|'.join(' '.join(row.get(key, '').split()).casefold() for key in IDENTITY)
    return 'review:' + sha(identity.encode())[:20]


def terminal(rows):
    """Original-action accounting convention used by B1P/B1O, unchanged."""
    found = {}
    for row in rows:
        if row['action'] != 'no_action_after_review':
            continue
        match = re.search(r'\bBatch B review ([A-Z]\d{3});', row['review_note'])
        rid = match[1] if match else None
        if row['decision_id'] in B1O_TERMINAL.values():
            prior_rid = next(k for k, v in B1O_TERMINAL.items() if v == row['decision_id'])
            assert rid in (None, prior_rid)
            assert row['review_note'].startswith(prior_rid + ' PROPOSE_CORRECTION_ACCEPTED:')
            rid = prior_rid
        if rid:
            assert rid not in found, f'Duplicate original-action terminal: {rid}'
            found[rid] = row['decision_id']
    return found


def accounting(rows, public):
    ledger = [row for row in decision_rows(load_queues()) if row['batch'] == 'B']
    closed = terminal(rows)
    pending = [row for row in ledger if row['review_id'] not in closed]
    active = [row for row in pending if row['paper_id'] in public]
    return {
        'historical_actions': len(ledger),
        'historical_papers': len({r['paper_id'] for r in ledger}),
        'historical_unresolved_actions': len(pending),
        'historical_unresolved_papers': len({r['paper_id'] for r in pending}),
        'active_public_unresolved_actions': len(active),
        'active_public_unresolved_papers': len({r['paper_id'] for r in active}),
        'closed_review_ids': sorted(closed),
        'historical_unresolved_review_ids': [r['review_id'] for r in pending],
        'active_public_unresolved_review_ids': [r['review_id'] for r in active],
    }


def acceptance_valid(rid, decision, paper, taxonomy):
    """Auditor's acceptance gate; no write and no shortcut from evidence alone."""
    source = source_record(rid)
    note = decision.get('review_note', '')
    return all((
        decision.get('decision_id') == IDS[rid] == decision_id(decision),
        decision.get('review_queue') == 'other', decision.get('target_type') == 'paper',
        decision.get('action') == 'no_action_after_review',
        decision.get('created_by') == 'maintainer-approved-batch-b-b1r',
        note.startswith(f'{rid} PROPOSE_CORRECTION_ACCEPTED: Batch B review {rid};'),
        POLICIES[rid] in note,
        source['official_manuscript']['sha256'] in note,
        'corpus_quality_batch_b_wave_b1q_2026_10_26' in note,
        ';'.join(TYPES[rid]) in note,
        all(decision.get(k) == paper[k] for k in ('title', 'year', 'doi', 'openalex_url')),
        paper['research_types'] == taxonomy['research_types'] == ';'.join(TYPES[rid]),
        taxonomy['research_types_status'] == 'reviewed',
        taxonomy['research_types_evidence_tier'] == 'primary_paper',
        bool(taxonomy['research_types_review_reason']),
        bool(taxonomy['research_types_evidence_excerpt']),
        source['official_manuscript']['url'] in taxonomy['research_types_evidence_source'],
    ))


@pytest.mark.parametrize('path,columns', [(PAPERS, PAPERS_COLUMNS), (TAXONOMY, PAPER_TAXONOMY_COLUMNS), (DECISIONS, REVIEW_DECISION_COLUMNS)])
def test_actual_csv_headers_keep_existing_schema(path, columns):
    assert tuple(next(csv.reader(io.StringIO((ROOT / path).read_text(), newline='')))) == columns


@pytest.mark.parametrize('path', [PAPERS, TAXONOMY])
def test_only_two_existing_records_and_exact_cell_allowlist_change(path):
    old_raw, new_raw = baseline(path), endpoint_bytes(path)
    old, new = csv_rows(old_raw), csv_rows(new_raw)
    ident = 'taxonomy_id' if path == TAXONOMY else 'paper_id'
    assert [r[ident] for r in old] == [r[ident] for r in new]
    assert {a['paper_id'] for a, b in zip(old, new) if a != b} == set(TARGETS.values())
    updates = {}
    for rid, pid in TARGETS.items():
        before, after = row_by_pid(old, pid), row_by_pid(new, pid)
        assert {k for k in before if before[k] != after[k]} == ALLOW[path]
        assert after['research_types'] == ';'.join(TYPES[rid])
        assert all(before[k] == after[k] for k in before if k not in ALLOW[path])
        assert before['tasks'] == after['tasks'] == 'detection'
        assert before['image_scopes'] == after['image_scopes'] == 'fully_generated'
        updates[pid] = {k: after[k] for k in ALLOW[path]}
    header = next(csv.reader(io.StringIO(old_raw.decode(), newline='')))
    chunks = logical_csv_chunks(old_raw)
    reconstructed = [chunks[0]] + [replace_csv_tokens(chunk, header, updates[row['paper_id']]) if row['paper_id'] in updates else chunk for row, chunk in zip(old, chunks[1:])]
    assert new_raw == b''.join(reconstructed), 'Unapproved CSV token bytes changed'
    assert sum(len(ALLOW[path]) for _ in TARGETS) == (2 if path == PAPERS else 12)


def test_101_prior_decision_rows_raw_prefix_preserved_with_only_two_terminal_appends():
    old_raw, new_raw = baseline(DECISIONS), endpoint_bytes(DECISIONS)
    old, new = csv_rows(old_raw), csv_rows(endpoint_bytes(DECISIONS))
    assert len(old) == 101
    assert len(new) == len({r['decision_id'] for r in new}) == 103
    assert new_raw.startswith(old_raw) and new[:-2] == old
    assert {r['decision_id'] for r in new[-2:]} == set(IDS.values())
    assert terminal(new) == {**terminal(old), **IDS}


@pytest.mark.parametrize('rid', TARGETS)
def test_actual_acceptance_conforms_to_schema_identity_policy_and_evidence(rid):
    rows = read_review_decisions(ROOT / DECISIONS)
    decision = next(r for r in rows if r['decision_id'] == IDS[rid])
    paper = row_by_pid(csv_rows((ROOT / PAPERS).read_bytes()), TARGETS[rid])
    taxonomy = row_by_pid(read_paper_taxonomy_registry(ROOT / TAXONOMY), TARGETS[rid])
    assert acceptance_valid(rid, decision, paper, taxonomy)
    assert decision['action'] in ALLOWED_REVIEW_ACTIONS and decision['review_queue'] in ALLOWED_REVIEW_QUEUES
    assert decision['created_at'] == decision['updated_at']
    assert datetime.fromisoformat(decision['created_at'].replace('Z', '+00:00')).tzinfo is not None
    assert 'no_action_after_review means the approved correction is complete' in decision['review_note']


@pytest.mark.parametrize('rid', TARGETS)
def test_real_registry_repeat_upsert_is_byte_identical_and_no_extra_decision(rid, tmp_path):
    raw = (ROOT / DECISIONS).read_bytes()
    target = tmp_path / 'review_decisions.csv'
    target.write_bytes(raw)
    row = next(r for r in read_review_decisions(target) if r['decision_id'] == IDS[rid])
    assert upsert_review_decision(row, path=target) == row
    assert upsert_review_decision(row, path=target) == row
    assert target.read_bytes() == raw


@pytest.mark.parametrize('rid', TARGETS)
@pytest.mark.parametrize('broken', ['types', 'action', 'identity', 'evidence', 'review_state'])
def test_acceptance_auditor_rejects_materially_incomplete_or_mismatched_decision(rid, broken):
    decision = deepcopy(next(r for r in read_review_decisions(ROOT / DECISIONS) if r['decision_id'] == IDS[rid]))
    paper = row_by_pid(csv_rows((ROOT / PAPERS).read_bytes()), TARGETS[rid])
    taxonomy = row_by_pid(read_paper_taxonomy_registry(ROOT / TAXONOMY), TARGETS[rid])
    if broken == 'types':
        taxonomy['research_types'] = source_record(rid)['current_authoritative_taxonomy']['research_types']
    elif broken == 'action':
        decision['action'] = 'exclude_paper_scope'
    elif broken == 'identity':
        decision['title'] = 'Unrelated paper'
    elif broken == 'evidence':
        decision['review_note'] = decision['review_note'].replace(source_record(rid)['official_manuscript']['sha256'], 'unverified')
    else:
        taxonomy['research_types_status'] = 'needs_review'
    assert not acceptance_valid(rid, decision, paper, taxonomy)


def test_only_original_two_actions_close_and_all_other_pending_questions_survive():
    public = published_context(PUBLISHED)['papers']
    before = accounting(csv_rows(baseline(DECISIONS)), public)
    after = accounting(csv_rows(endpoint_bytes(DECISIONS)), public)
    assert set(after['closed_review_ids']) - set(before['closed_review_ids']) == set(TARGETS)
    for key in ('historical_unresolved_review_ids', 'active_public_unresolved_review_ids'):
        assert after[key] == [r for r in before[key] if r not in TARGETS]
    assert {k: after[k] for k in ('historical_actions', 'historical_papers')} == {'historical_actions': 159, 'historical_papers': 148}
    assert after['historical_unresolved_actions'] == before['historical_unresolved_actions'] - 2 == 131
    assert after['active_public_unresolved_actions'] == before['active_public_unresolved_actions'] - 2 == 129
    # Unique affected-paper counts are independently derived, not decremented blindly.
    assert after['historical_unresolved_papers'] == 121
    assert after['active_public_unresolved_papers'] == 119
    ledger = list(decision_rows(load_queues()))
    for rid, pid in TARGETS.items():
        assert [(r['review_id'], r.get('dimension')) for r in ledger if r['batch'] == 'B' and r['paper_id'] == pid] == [(rid, 'research_types')]
    assert {'R234', 'T046', 'T093', 'T608', 'T526', 'P526'} <= set(after['historical_unresolved_review_ids'])


@pytest.mark.parametrize('path', BASELINE['evidence_sha256'])
def test_B1Q_packet_is_unmodified_with_all_original_limitations_history_and_corrections(path):
    assert sha((ROOT / path).read_bytes()) == BASELINE['evidence_sha256'][path]
    assert packet()['evidence_only'] is True
    assert set(packet()['review_ids']) == set(TARGETS)
    for rid in TARGETS:
        source = source_record(rid)
        assert source['maintainer_acceptance'] == 'PENDING'
        assert source['authoritative_change_applied'] is False
        assert source['original_action_remains_open'] is True
        assert source['official_manuscript']['sha256'] in (ROOT / path).read_text()


def test_locked_R2_R3_are_exact_B1Q_policy_snapshot_and_original_questions_unchanged():
    policies = json.loads((ROOT / 'data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json').read_bytes())
    live = {p['policy_id']: p for p in policies['policies']}
    snapshot = packet()['locked_policies']
    # The outer B1Q object stores the complete selected policy records.
    for rid, policy in POLICIES.items():
        value = snapshot[policy] if isinstance(snapshot, dict) and policy in snapshot else next(p for p in snapshot if p['policy_id'] == policy)
        assert value == live[policy]
        original = source_record(rid)['original_Batch_B_action']
        actual = next(r for r in decision_rows(load_queues()) if r['review_id'] == rid)
        assert original == actual
    prefix = 'data/raw/corpus_quality_audit_2026_10_04/'
    for name in ('unmapped_papers', 'taxonomy_review', 'relationship_review', 'publication_metadata_review', 'batch_c_policy_decisions'):
        path = prefix + name + '.json'
        assert (ROOT / path).read_bytes() == baseline(path)


def test_all_49_frozen_NeurIPS_receipts_and_original_blocked_status_remain_unchanged():
    path = 'data/raw/systematic_gap_migration_2026_10_03/baseline.json'
    assert (ROOT / path).read_bytes() == baseline(path)
    frozen = json.loads((ROOT / path).read_bytes())['frozen_sha256']
    assert len(frozen) == 49
    for p, fingerprint in frozen.items():
        assert sha(preserved_bytes(ROOT, p)) == fingerprint
    assert packet()['neurips_status'] == '7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA'


@lru_cache
def context():
    return load_context()


@pytest.mark.parametrize('path', FROZEN['pre_export_frozen_source_sha256'])
def test_all_accepted_source_bytes_and_B1Q_B1R_reports_survive_controlled_export(path):
    # Only two mutable operational files have an accepted historical hash.
    # B1Q/B1R evidence and the unchanged authoritative taxonomy stay live.
    observed = endpoint_bytes(path) if path in {PAPERS, DECISIONS} else (ROOT / path).read_bytes()
    assert sha(observed) == FROZEN['pre_export_frozen_source_sha256'][path]


def test_public_paper_delta_is_exactly_two_types_and_review_reason_updates_with672_unchanged():
    before, after = published_context(BASE), published_context(PUBLISHED)
    assert before['papers'].keys() == after['papers'].keys()
    assert len(after['papers']) == 674
    changed = {pid for pid in before['papers'] if before['papers'][pid] != after['papers'][pid]}
    assert changed == set(TARGETS.values())
    assert sum(before['papers'][pid] == after['papers'][pid] for pid in before['papers'] if pid not in changed) == 672
    for rid, pid in TARGETS.items():
        expected = deepcopy(before['papers'][pid])
        expected['research_types'] = TYPES[rid]
        expected['taxonomy_review']['research_types']['reason'] = after['taxonomy'][pid]['research_types_review_reason']
        assert after['papers'][pid] == expected
        authoritative = public_taxonomy_fields(after['taxonomy'][pid])
        assert all(after['papers'][pid][key] == value for key, value in authoritative.items())
        assert after['papers'][pid]['tasks'] == ['detection']
        assert after['papers'][pid]['image_scopes'] == ['fully_generated']


def test_public_map_delta_is_exactly_seven_existing_dependents_with_all1410_identities_preserved():
    before = {r['id']: r for r in json.loads(baseline(PUBLIC[1]))['records']}
    after = {r['id']: r for r in json.loads(endpoint_bytes(PUBLIC[1]))['records']}
    assert len(before) == len(after) == 1410 and before.keys() == after.keys()
    changed = {rid for rid in before if before[rid] != after[rid]}
    dependents = {rid for rid, row in before.items() if row.get('paper_id') in TARGETS.values()}
    assert changed == dependents and len(changed) == 7
    assert Counter(before[rid]['paper_id'] for rid in changed) == Counter({TARGETS['R026']: 4, TARGETS['R253']: 3})
    inverse = {pid: rid for rid, pid in TARGETS.items()}
    for rid, row in before.items():
        expected = deepcopy(row)
        if rid in dependents:
            pid = row['paper_id']
            expected['research_types'] = TYPES[inverse[pid]]
            expected['taxonomy_review']['research_types']['reason'] = published_context(PUBLISHED)['taxonomy'][pid]['research_types_review_reason']
        assert after[rid] == expected
    assert published_context(BASE)['pairs'] == published_context(PUBLISHED)['pairs']
    assert sum(published_context(PUBLISHED)['pairs'].values()) == len(published_context(PUBLISHED)['pairs']) == 1410


def test_paired_export_metadata_changes_only_UTC_generation_timestamp():
    timestamps = []
    for path in PUBLIC:
        before, after = json.loads(baseline(path)), json.loads(endpoint_bytes(path))
        old_meta, new_meta = deepcopy(before['metadata']), deepcopy(after['metadata'])
        old_time, new_time = old_meta.pop('public_preview_generated_at'), new_meta.pop('public_preview_generated_at')
        assert old_meta == new_meta and new_time >= old_time
        timestamps.append(new_time)
        assert {k: v for k, v in before.items() if k not in {'records', 'metadata'}} == {k: v for k, v in after.items() if k not in {'records', 'metadata'}}
    assert timestamps[0] == timestamps[1]
    from scripts.public_export_metadata import is_utc_timestamp
    assert is_utc_timestamp(timestamps[0])


def test_recomputed_source_and_export_totals_match_with_only_R3_R2_additions():
    before, after = published_context(BASE), context()
    def public_totals(papers):
        return Counter(label for row in papers.values() for dim in ('tasks', 'research_types') for label in row[dim])
    old_totals, live_totals = public_totals(before['papers']), public_totals(after['papers'])
    source_totals = Counter(label for row in after['taxonomy'].values() for dim in ('tasks', 'research_types') for label in row[dim].split(';') if label)
    assert old_totals - live_totals == {} and live_totals - old_totals == {'benchmark': 1, 'analysis_study': 1}
    assert live_totals == source_totals == CURRENT_TAXONOMY_TOTALS
    assert live_totals == Counter(detection=621, source_attribution=84, localization=45, method=578, dataset=138, benchmark=97, survey=21, analysis_study=86)
    assert before['counts'] == after['counts'] == CURRENT_CORPUS_COUNTS
    assert after['counts'] == {'public': 674, 'formal': 557, 'mapped': 613, 'unmapped': 61, 'relationship_rows': 1410, 'unique_paper_institution_pairs': 1410}
    for dim in ('tasks', 'image_scopes'):
        assert {pid: r[dim] for pid, r in before['papers'].items()} == {pid: r[dim] for pid, r in after['papers'].items()}


def test_no_authoritative_paper_institution_publication_task_or_scope_data_changes_beyond_B1R():
    paths = subprocess.check_output(['git', '--no-optional-locks', 'ls-tree', '-r', '--name-only', BASE, '--', 'data/curated', 'data/manual'], cwd=ROOT, text=True).splitlines()
    allowed = {PAPERS, TAXONOMY, DECISIONS, 'data/manual/key_paper_coverage_report.csv', 'data/manual/missing_author_mappings_report.csv'}
    for path in paths:
        if path not in allowed:
            assert endpoint_bytes(path) == baseline(path), path
    before, after = csv_rows(baseline(PAPERS)), csv_rows(endpoint_bytes(PAPERS))
    for old, new in zip(before, after):
        assert {k: v for k, v in old.items() if k != 'research_types'} == {k: v for k, v in new.items() if k != 'research_types'}


def test_public_frontend_assets_are_unchanged_and_only_paired_data_files_change_under_web():
    changed = set(subprocess.check_output(['git', '--no-optional-locks', 'diff', '--name-only', BASE, '--', 'web'], cwd=ROOT, text=True).splitlines())
    assert changed == set(PUBLIC)
    assert set(context()['papers']) == set(published_context(BASE)['papers'])
    for paper in context()['papers'].values():
        for dimension in ('tasks', 'image_scopes', 'research_types'):
            assert isinstance(paper[dimension], list)
        assert set(paper['taxonomy_review']) == {'tasks', 'image_scopes', 'research_types'}
