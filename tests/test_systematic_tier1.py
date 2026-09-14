"""Tier 1 curation must preserve identities, paper-time affiliations and history."""
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from scripts.report_systematic_tier1 import CSV, REPORT, make_rows, diff_audit, corpus_stats, render, read_csv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/processed/systematic_tier1_2026_09'


def proposals():
    return json.loads((OUT / 'proposals.json').read_text())['papers']


def test_all_sixteen_decisions_and_exported_fields():
    rows = make_rows()
    assert len(rows) == 16
    assert read_csv(CSV) == rows
    assert {r['outcome'] for r in rows} == {'MISSING_ADD'}
    assert len({r['paper_id'] for r in rows}) == 16


def test_existing_authoritative_rows_and_frontend_unchanged():
    assert all(d['existing_rows_changed'] == 0 for n, d in diff_audit().items() if n != 'frontend')


def test_dacom_complete_author_order_and_seventh_affiliation():
    p = next(p for p in proposals() if p['candidate_id'] == 'audit:708c69744d1ea0ed')
    assert p['authors'] == ['Bin Li', 'Haoyu Li', 'Haodong Li', 'Jiaming Zhong', 'Changsheng Chen', 'Jiangqun Ni', 'Bo Cao']
    assert next(a for a in p['affiliations'] if 'Bo Cao' in a['authors'])['institution'] == 'Smart City Research Institute of China Electronics Technology Group Corporation'


def test_detective_workshop_not_inserted_separately():
    records = json.loads((ROOT / 'web/data/public_preview_papers.json').read_text())['records']
    found = [p for p in records if p['title'].startswith('Detective SAM:')]
    assert len(found) == 1 and found[0]['year'] == 2026
    assert len(found[0]['authors']) == 6


def test_fuse_southeast_entities_are_distinct_and_no_guessed_coordinates():
    institutions = read_csv(ROOT / 'data/curated/institutions.csv')
    bd = next(i for i in institutions if i['canonical_name'] == 'Southeast University (Bangladesh)')
    cn = next(i for i in institutions if i['canonical_name'] == 'Southeast University')
    assert bd['institution_id'] != cn['institution_id']
    fuse = next(p for p in proposals() if p['title'].startswith('FUSE:'))
    assert bd['institution_id'] in {a['institution_id'] for a in fuse['affiliations']}
    assert cn['institution_id'] not in {a['institution_id'] for a in fuse['affiliations']}
    assert not any(l['institution_id'] == bd['institution_id'] for l in read_csv(ROOT / 'data/curated/institution_locations.csv'))


def test_ntire_email_and_team_only_authors_are_not_mapped():
    p = next(p for p in proposals() if p['title'].startswith('NTIRE'))
    assert len(p['authors']) == 54
    rows = [r for r in read_csv(ROOT / 'data/curated/author_institution_mappings.csv') if r['paper_id'] == p['paper_id']]
    mapped = {a.strip() for r in rows for a in r['institution_authors'].split(';')}
    assert not mapped.intersection(p['authors'][24:29])
    assert 'Cong Luo' not in mapped and 'Mikhail Erofeev' not in mapped
    assert 'Fei Wu' in mapped


def test_final_duplicate_exclusion_and_coverage_totals():
    assert corpus_stats() == {'public': 636, 'published': 528, 'mapped': 623, 'markers': 1466, 'duplicate_identity_pairs': [], 'active_exclusion_leaks': 0}


def test_tier1_report_reproduces_and_historical_decisions_unchanged():
    assert REPORT.read_text() == render(read_csv(CSV), corpus_stats(), diff_audit())
    for path in ('data/manual/systematic_literature_completeness_candidates_2026_09.csv', 'docs/systematic_literature_completeness_audit_2026_09.md'):
        assert (ROOT / path).read_bytes() == (OUT / 'baseline' / path).read_bytes()
