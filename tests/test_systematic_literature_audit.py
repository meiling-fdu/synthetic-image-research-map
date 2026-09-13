"""Audit accounting must conserve provenance and leave the corpus frozen."""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import report_systematic_literature as audit
from collect_systematic_literature import PROCESSED, ROOT, read_response
from screen_systematic_literature import STATUSES


def rows():
    return audit.read_csv(audit.CANONICAL)


def test_status_vocabulary_and_unique_work_ids():
    data = rows()
    assert len({r['candidate_id'] for r in data}) == len(data)
    assert set(r['final_status'] for r in data) <= set(STATUSES)
    assert all(r['rationale'] for r in data if r['final_status'].startswith('AMBIGUOUS'))
    assert all(r['matched_exclusion_id'] for r in data if r['final_status'] == 'EXISTING_EXCLUSION')
    identifiers = defaultdict(set)
    for row in data:
        for key in ('doi', 'arxiv_id', 'openalex_id', 'matched_corpus_paper_id'):
            for value in row[key].split(' | '):
                if value:
                    identifiers[key, value].add(row['candidate_id'])
    assert all(len(owners) == 1 for owners in identifiers.values())


def test_every_selected_observation_preserves_provenance():
    observations = json.loads((PROCESSED / 'observations.json').read_text())
    data = rows()
    assert sum(int(r['observation_count']) for r in data) == len(observations)
    for row in data:
        provenance = json.loads(row['observation_provenance'])
        assert len(provenance) == int(row['observation_count'])
        assert '+'.join(sorted({o['channel'] for o in provenance})) == row['discovery_channels']
        assert all(o['discovery_source'] and o['raw_path'] and o['discovery_pass'] for o in provenance)


def test_high_confidence_requires_title_matched_primary_and_explicit_decision():
    from reconcile_systematic_literature import compact_title
    primary = json.loads((PROCESSED / 'primary_evidence.json').read_text())
    decisions = {compact_title(k): v for k, v in json.loads((PROCESSED / 'adjudications.json').read_text()).items()}
    for row in rows():
        if row['final_status'] != 'CANDIDATE_ADD_HIGH_CONFIDENCE':
            continue
        assert not row['matched_corpus_paper_id'] and not row['matched_exclusion_id']
        assert row['scope_evidence'] and row['identity_evidence']
        assert all(row[k] for k in ('proposed_forensic_task', 'proposed_image_scope', 'proposed_research_type'))
        assert decisions[compact_title(row['canonical_title'])]['final_status'] == row['final_status']
        assert any(p['primary_url'] in row['primary_evidence_url'].split(' | ')
                   and compact_title(p['title']) == compact_title(row['canonical_title'])
                   and len(p['abstract']) > 100 for p in primary)


def test_survey_reference_accounting_is_complete():
    surveys = audit.accounting(rows())['surveys']
    assert sum(s['enumerated'] for s in surveys) == 640
    assert next(s for s in surveys if s['kind'] == 'survey_pdf')['enumerated'] == 135
    assert all(sum(s['reference_outcomes'].values()) == s['enumerated'] for s in surveys)


def test_channel_overlap_counts_each_work_once():
    data = rows()
    assert sum(audit.overlaps(data).values()) == len(data)
    assert audit.overlaps(data) == {k: Counter(r['discovery_channels'] for r in data)[k] for k in audit.overlaps(data)}


def test_active_exclusions_never_become_additions():
    data = rows()
    assert any(r['matched_exclusion_id'] for r in data)
    assert all(r['final_status'] in {'EXISTING_EXCLUSION', 'EXISTING_CURRENT', 'EXISTING_ALTERNATE_TITLE'} for r in data if r['matched_exclusion_id'])
    # A duplicate-record exclusion may share a title with the retained canonical work.
    retained = [r for r in data if r['matched_exclusion_id'] and r['matched_corpus_paper_id']]
    assert [r['canonical_title'] for r in retained] == ['Source Generator Attribution via Inversion']
    for fragment in ('Stable Signature', 'AutoSplice', 'FaceForensics++'):
        assert any(fragment.casefold() in r['canonical_title'].casefold() and r['final_status'] == 'EXISTING_EXCLUSION' for r in data)


def test_report_and_statistics_reproduce_from_canonical_registry():
    data = rows()
    stats = audit.accounting(data)
    assert audit.REPORT.read_text() == audit.render(data, stats, audit.CANONICAL)
    stored = json.loads((PROCESSED / 'audit_statistics.json').read_text())
    assert stored == {k: v for k, v in stats.items() if k != 'sources'}


def test_index_download_is_not_claimed_as_full_semantic_enumeration():
    proceedings = audit.accounting(rows())['proceedings']
    assert all(p['coverage_level'] == 'BOUNDED_SEARCH' for p in proceedings)
    main = next(p for p in proceedings if 'vol38-main-conference' in p['source'])
    assert main['enumerated'] == 5823 and main['track'] == 'Main Conference'
    assert any(p.get('track') == 'Creative AI only' and p['enumerated'] == 64 for p in proceedings)


def test_frozen_pre_audit_files_are_byte_identical():
    baseline = json.loads((PROCESSED / 'baseline_sha256.json').read_text())
    assert len(baseline) == 670
    assert [path for path, sha in baseline.items() if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != sha] == []


def test_successful_cache_responses_have_verified_checksums():
    for source in audit.source_logs():
        if source['status'] == 200:
            assert read_response(source)
