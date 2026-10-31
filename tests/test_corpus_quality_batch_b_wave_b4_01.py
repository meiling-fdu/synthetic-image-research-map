"""B4-01 URL-specific acceptance rules; public export remains a later phase.

B4 accounting is checked at its immutable registry endpoint, so later unrelated
accepted reviews do not become failures of this historical transaction.
"""
from copy import deepcopy
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

import pytest

from scripts.curated_export import _curated_paper_record, _merge_curated_paper
from scripts.export_public_preview import (
    apply_publication_overrides, normalize_exported_paper_identifiers,
    reconstruct_publication_links, add_public_detail_fields,
    synchronize_public_authors, detail_paper_identity,
    load_institution_author_overrides, DEFAULT_CURATED_AUTHOR_OVERRIDES,
)
from scripts.paper_links import resolve_public_links
from scripts.review_decisions import read_review_decisions, upsert_review_decision
from scripts.validate_corpus_quality_audit import decision_rows, load_context, load_queues

ROOT = Path(__file__).resolve().parents[1]
BASE = '7fc8ceae702324628335944cf4b545a3733fdc56'
REL = 'data/raw/corpus_quality_batch_b_wave_b4_01_2026_10_29/adjudication_manifest.json'
MANIFEST = json.loads((ROOT / REL).read_text())
RECORDS = {r['review_id']: r for r in MANIFEST['records']}
ACCEPTED = ['P034', 'P254', 'P305', 'P097', 'P105', 'P150', 'P177', 'P229']
IDENTITY = ('review_queue', 'target_type', 'doi', 'openalex_url', 'title', 'year', 'institution')


def sha(value):
    return hashlib.sha256(value).hexdigest()


def canonical_hash(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())


def baseline(path):
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT)


def rows(path):
    with (ROOT / path).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def source_row(record):
    binding = record['binding']
    if binding['target_path'].endswith('papers.csv'):
        found = [r for r in rows(binding['target_path']) if r['paper_id'] == record['paper_id']]
    else:
        title = binding['canonical_identity']['title']
        found = [r for r in rows(binding['target_path']) if r['title'] == title]
    assert len(found) == 1
    return found[0]


def evidence_url(record):
    raw = record['b3_evidence_record']['reviewer_evidence_record']
    if record['review_id'] in ('P254', 'P305'):
        name = 'f46eff9ea9746db9e65a' if record['review_id'] == 'P254' else 'ff2f99328559d41a9b09'
        message = json.loads((ROOT / f'data/raw/venue_audit_crossref/{name}.json').read_text())['response']['message']
        return message['resource']['primary']['URL']
    return (raw.get('identity_evidence', {}).get('formal_url')
            or raw.get('verified_official_landing_url') or raw.get('proposed_formal_url'))


def acceptance_valid(record, decision):
    binding = record['binding']
    identity = binding['canonical_identity']
    accepted = record['accepted']
    raw = json.dumps(record['b3_evidence_record'], indent=2, ensure_ascii=False).encode() + b'\n'
    expected_id = 'review:' + sha('|'.join(' '.join(str(decision.get(k, '')).split()).casefold() for k in IDENTITY).encode())[:20]
    note = decision.get('review_note', '')
    if not all((
        decision.get('decision_id') == record['native_id'] == expected_id,
        decision.get('review_queue') == 'publication_venues',
        decision.get('target_type') == 'paper',
        decision.get('created_by') == 'maintainer-approved-batch-b-b4-01',
        decision.get('action') == ('no_action_after_review' if accepted else 'unresolved'),
        all(decision.get(k) == str(identity[k]) for k in ('title', 'year', 'doi', 'openalex_url')),
        note.startswith('Batch B review ' + record['review_id'] + ';'),
        binding['review_id'] == record['review_id'],
        binding['baseline_commit'] == BASE,
        record['binding_sha256'] == canonical_hash(binding),
        '[publication-url-state:' + record['binding_sha256'] + ']' in note,
        binding['b3_record_sha256'] == sha(raw),
        binding['b3_record_sha256'] in note,
        '[venue-state:' not in note,
    )):
        return False
    current = source_row(record)
    if accepted:
        return all((binding['accepted_url'] == record['accepted_stored_url'] == evidence_url(record),
                    current[binding['target_field']] == binding['accepted_url'],
                    binding['accepted_url'] in note,
                    record['b3_evidence_record']['provisional_outcome'] == 'SUPPORTED_ADDITION'))
    return (record['review_id'] == 'P028' and binding['accepted_url'] is None
            and current['paper_url'] == binding['before_url']
            and record['b3_evidence_record']['provisional_outcome'] == 'EVIDENCE_INSUFFICIENT'
            and 'do not infer nonpublication' in note)


@pytest.mark.parametrize('rid', list(RECORDS))
def test_all_nine_formal_decisions_satisfy_url_specific_acceptance(rid):
    record = RECORDS[rid]
    found = [r for r in read_review_decisions() if r['decision_id'] == record['native_id']]
    assert len(found) == 1
    assert found[0] == record['formal_decision']
    assert acceptance_valid(record, found[0])


@pytest.mark.parametrize('rid', ACCEPTED)
def test_current_authoritative_url_and_identity_fields_match_acceptance(rid):
    record = RECORDS[rid]
    current = source_row(record)
    identity = record['binding']['canonical_identity']
    if record['binding']['target_path'].endswith('papers.csv'):
        original = next(r for r in csv.DictReader(io.StringIO(baseline('data/curated/papers.csv').decode(), newline='')) if r['paper_id'] == record['paper_id'])
        assert {k:v for k,v in current.items() if k != 'paper_url'} == {k:v for k,v in original.items() if k != 'paper_url'}
        links = resolve_public_links(current)
    else:
        original = deepcopy(record['b3_evidence_record']['current_identity'])
        assert str(current['formal_year']) == str(original['year']) == current['match_year']
        assert current['formal_venue'] == original['venue']
        assert current['formal_doi'] == original['doi']
        assert current['publication_type'] == original['publication_type']
        apply_publication_overrides([original], [{**current, 'match_year':int(current['match_year']), 'formal_year':int(current['formal_year'])}])
        links = resolve_public_links(original)
    assert links['formal_url'] == record['accepted_stored_url']
    assert links['formal_doi'] == ''  # Landing URLs do not replace the existing source DOI.
    assert links['arxiv_id'] == identity['arxiv_id']


@pytest.mark.parametrize('rid', ACCEPTED)
def test_targeted_merge_is_only_public_link_state_in_memory(rid):
    record = RECORDS[rid]
    # Compare the SAME pipeline stage on both branches. _merge_curated_paper
    # normally flattens some decorated author objects before detail enrichment.
    public = json.loads(baseline('web/data/public_preview_papers.json'))['records']
    original = next(p for p in public if p.get('arxiv_id') == record['binding']['canonical_identity']['arxiv_id'])
    before, after = deepcopy(original), deepcopy(original)
    current = source_row(record)
    if record['binding']['target_path'].endswith('papers.csv'):
        old = next(r for r in csv.DictReader(io.StringIO(baseline('data/curated/papers.csv').decode(), newline='')) if r['paper_id'] == record['paper_id'])
        _merge_curated_paper(before, _curated_paper_record(old, before['tasks']))
        _merge_curated_paper(after, _curated_paper_record(current, after['tasks']))
    else:
        apply_publication_overrides([after], [{**current, 'match_year':int(current['match_year']), 'formal_year':int(current['formal_year'])}])
    normalize_exported_paper_identifiers([before, after])
    reconstruct_publication_links([before, after])
    allowed = {'paper_url','formal_url','primary_url','url','landing_page_url','is_arxiv_preprint','notes'}
    assert {k:v for k,v in before.items() if k not in allowed} == {k:v for k,v in after.items() if k not in allowed}
    names = lambda values: [v.get('name') if isinstance(v, dict) else v for v in values]
    assert before['authors'] == after['authors']
    assert names(before['authors']) == names(original['authors'])
    assert resolve_public_links(after)['formal_url'] == record['accepted_stored_url']


@pytest.mark.parametrize('rid', ['P034', 'P105'])
def test_downstream_detail_restores_exact_structured_authors_and_markers(rid):
    record = RECORDS[rid]
    public = json.loads(baseline('web/data/public_preview_papers.json'))['records']
    maps = json.loads(baseline('web/data/public_preview_map_data.json'))['records']
    original = next(p for p in public if p.get('paper_id') == record['paper_id'])
    markers = [m for m in maps if detail_paper_identity(m) == detail_paper_identity(original)]
    assert len(markers) == (7 if rid == 'P034' else 6)
    before, after = deepcopy(original), deepcopy(original)
    before_maps, after_maps = deepcopy(markers), deepcopy(markers)
    old = next(r for r in csv.DictReader(io.StringIO(baseline('data/curated/papers.csv').decode(), newline='')) if r['paper_id'] == record['paper_id'])
    _merge_curated_paper(before, _curated_paper_record(old, before['tasks']))
    _merge_curated_paper(after, _curated_paper_record(source_row(record), after['tasks']))
    assert before['authors'] == after['authors']
    overrides = load_institution_author_overrides(DEFAULT_CURATED_AUTHOR_OVERRIDES)
    add_public_detail_fields([before], before_maps, overrides)
    add_public_detail_fields([after], after_maps, overrides)
    synchronize_public_authors([before], before_maps)
    synchronize_public_authors([after], after_maps)
    assert before['authors'] == after['authors'] == original['authors']
    assert before_maps == after_maps


def test_url_only_decisions_do_not_confirm_venue_type_or_track():
    from scripts.venue_audit import VenueAudit
    audit = VenueAudit([], evidence=[], decisions=[r['formal_decision'] for r in RECORDS.values()])
    assert not audit.confirmations
    assert not audit.explicit_conflicts


def test_prior_registry_prefix_and_all_prior_decisions_are_preserved():
    raw = (ROOT / 'data/curated/review_decisions.csv').read_bytes()
    old = baseline('data/curated/review_decisions.csv')
    assert raw.startswith(old)
    all_rows = read_review_decisions()
    old_rows = list(csv.DictReader(io.StringIO(old.decode(), newline='')))
    assert len(old_rows) == 103 and all_rows[:103] == old_rows
    assert len(all_rows) >= 112
    assert {r['decision_id'] for r in all_rows[103:112]} == {r['native_id'] for r in RECORDS.values()}
    assert len(all_rows) == len({r['decision_id'] for r in all_rows})


def test_eight_resolved_and_hold_at_immutable_b4_registry_endpoint():
    endpoint = read_review_decisions()[:112]
    special = {'review:b9f458d69de24b8aae0a':'R267','review:aa32e93a24ade10ed99d':'R236'}
    terminal = {}
    for row in endpoint:
        if row['action'] != 'no_action_after_review':
            continue
        match = re.search(r'\bBatch B review ([A-Z]\d{3});', row['review_note'])
        rid = match[1] if match else special.get(row['decision_id'])
        if rid:
            assert rid not in terminal
            terminal[rid] = row
    for rid in ACCEPTED:
        assert acceptance_valid(RECORDS[rid], terminal[rid])
    assert 'P028' not in terminal and len(terminal) == 36
    ledger = [r for r in decision_rows(load_queues()) if r['batch'] == 'B']
    pending = [r for r in ledger if r['review_id'] not in terminal]
    active_ids = set(MANIFEST['active_public_ids_at_adjudication'])
    active = [r for r in pending if r['paper_id'] in active_ids]
    assert len(ledger) == 159 and len(active_ids) == 674
    assert (len(pending),len({r['paper_id'] for r in pending})) == (123,113)
    assert (len(active),len({r['paper_id'] for r in active})) == (121,111)
    assert 'P028' in {r['review_id'] for r in pending}


@pytest.mark.parametrize('rid', list(RECORDS))
def test_native_repeat_upsert_is_byte_identical(rid, tmp_path):
    target = tmp_path / 'review_decisions.csv'
    initial = (ROOT / 'data/curated/review_decisions.csv').read_bytes()
    target.write_bytes(initial)
    row = RECORDS[rid]['formal_decision']
    assert upsert_review_decision(row,path=target) == row
    assert upsert_review_decision(row,path=target) == row
    assert target.read_bytes() == initial


@pytest.mark.parametrize('kind', ['wrong_url','wrong_action','wrong_identity','missing_binding','wrong_evidence','broad_venue_confirmation'])
def test_acceptance_rejects_incomplete_or_mismatched_decisions(kind):
    record = deepcopy(RECORDS['P034']);decision = deepcopy(record['formal_decision'])
    if kind == 'wrong_url':
        record['binding']['accepted_url'] = RECORDS['P097']['accepted_stored_url']
    elif kind == 'wrong_action':
        decision['action'] = 'unresolved'
    elif kind == 'wrong_identity':
        decision['title'] = 'Unrelated paper'
    elif kind == 'missing_binding':
        decision['review_note'] = decision['review_note'].replace(record['binding_sha256'],'missing')
    elif kind == 'wrong_evidence':
        record['binding']['b3_record_sha256'] = '0'*64
    else:
        decision['review_note'] += ' [venue-state:unrelated]'
    assert not acceptance_valid(record,decision)


def test_p034_author_and_b1m_version_caveats_not_conflated():
    record = RECORDS['P034'];raw = record['b3_evidence_record']['reviewer_evidence_record']
    assert raw['identity_evidence']['canonical_author_count'] == 12
    assert raw['identity_evidence']['publisher_author_count'] == 13
    assert 'Manni Cui' in raw['identity_evidence']['author_difference']
    assert len(record['binding']['canonical_identity']['authors']) == 12
    assert 'Manni Cui' not in record['binding']['canonical_identity']['authors']
    assert 'No author' in raw['identity_evidence']['author_difference']
    assert record['formal_decision']['action'] == 'no_action_after_review'
    assert raw['scientific_review_restarted'] is False
