"""B5-02 current-state gates: exact approved B4-03 source and public evolution.

Historical transaction assertions remain independent authenticated checkpoints.
These live gates reject unrelated source, identity, taxonomy and map changes.
"""
from collections import Counter
from copy import deepcopy
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

import pytest

R=Path(__file__).resolve().parents[1]
ARCHIVE=R/'data/raw/corpus_quality_batch_b_wave_b5_02_2026_11_01'
O=R/'data/raw/corpus_quality_batch_b_wave_b4_03_2026_11_01'
B=ARCHIVE/'evidence_archive/b3_03'
BASE='d109c70f6994906ec3d9197baad51cf9d8e51f7c'
from scripts.review_decisions import read_review_decisions, upsert_review_decision
from scripts.venue_audit import confirmation_fingerprint, VenueAudit
from scripts.validate_corpus_quality_audit import load_context, load_queues, decision_rows
from scripts.paper_taxonomy_registry import read_paper_taxonomy_registry
from tests.corpus_quality_test_helpers import published_bytes, published_context

P='data/curated/papers.csv';T='data/curated/paper_taxonomy.csv';D='data/curated/review_decisions.csv'
TYPES={'R110':'method;dataset;benchmark','R171':'method;dataset;benchmark',
       'R256':'method;dataset;benchmark','R275':'method;benchmark','R564':'method;dataset'}
ACCEPTED=set(TYPES)|{'P231'}
HOLDS={'R138','R154','R161','R187','R231'}
IDENTITY=('review_queue','target_type','doi','openalex_url','title','year','institution')
M=json.loads((O/'adjudication_manifest.json').read_text())
CASES={r['review_id']:r for r in M['records']}
MATRIX=json.loads((B/'batch_dispositions.json').read_text())
EVIDENCE={r['review_id']:r for r in MATRIX['records']}


def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(a):return json.dumps(a,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def csv_rows(raw):return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'),newline='')))
def old(path):return subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=R)
def current(path):return (R/path).read_bytes()
def native(row):return 'review:'+sha('|'.join(' '.join(str(row.get(k,'')).split()).casefold() for k in IDENTITY).encode())[:20]
def maps(path,key,raw=None):return {r[key]:r for r in csv_rows(raw if raw is not None else current(path))}


def valid_case(case, decision=None, paper=None, taxonomy=None):
    """Require original evidence, independently authorized state and exact formal row."""
    rid=case['review_id'];ev=EVIDENCE[rid];binding=case['binding']
    d=decision if decision is not None else case['formal_decision']
    p=paper if paper is not None else maps(P,'paper_id').get(case['paper_id'])
    t=taxonomy if taxonomy is not None else maps(T,'taxonomy_id')[case['taxonomy_id']]
    # Approval is tied to the exact original question, sources and baseline,
    # never merely to a matching self-supplied hash or note token.
    assert rid in ACCEPTED|HOLDS
    assert binding['baseline_commit']==BASE and binding['review_id']==rid
    ledger={r['review_id']:r for r in decision_rows(load_queues(R)) if r['batch']=='B'}
    assert binding['original_question']==ledger[rid]
    assert binding['B3_matrix_sha256']==sha((B/'batch_dispositions.json').read_bytes())
    assert binding['B3_record_sha256']==ev['evidence_record_sha256']==sha((B/ev['evidence_record']).read_bytes())
    assert binding['B3_record_path']==ev['evidence_record']
    assert case['source_provenance']==ev['source_provenance']
    assert case['scientific_limitations']==ev['limitations']
    assert case['binding_sha256']==sha(canonical(binding))
    assert f'[b4-03-state:{case["binding_sha256"]}]' in d['review_note']
    assert binding['B3_matrix_sha256'] in d['review_note'] and binding['B3_record_sha256'] in d['review_note']
    assert d==case['formal_decision'] and native(d)==case['native_id']==d['decision_id']
    assert d['review_queue']==('publication_venues' if rid=='P231' else 'other')
    assert d['action']==('no_action_after_review' if rid in ACCEPTED else 'unresolved')
    assert d['created_by']=='maintainer-approved-batch-b-b4-03'
    assert d['review_note'].startswith(f'Batch B review {rid};')
    assert d['target_type']=='paper' and not d['institution']
    assert d['created_at']==d['updated_at'] and re.fullmatch(r'2026-11-01T\d\d:\d\d:\d\dZ',d['created_at'])
    assert case['accepted']==binding['accepted']==(rid in ACCEPTED)
    ref=published_context(BASE)['papers'][case['paper_id']]
    for k in ('title','doi','year','openalex_url'):
        assert str(d.get(k) or '')==str(ref.get(k) or '')
    assert binding['canonical_bibliographic_identity']['authors']==ref['authors']
    assert case['empirical_results_independently_reproduced'] is False
    if rid in TYPES:
        assert case['disposition']==binding['disposition']=='ACCEPTED'
        assert t['research_types']==TYPES[rid]
        for k in ('research_types_review_reason','research_types_evidence_source','research_types_evidence_excerpt'):
            assert t[k] and t[k]==binding['expected_after_state']['taxonomy'][k]
        assert t['research_types_evidence_tier']=='primary_paper'
        assert t['audited_at']=='2026-11-01'
        assert binding['policy_ids']==ev['governing_policy_ids']
        assert binding['accepted_changes']
        if rid=='R564':
            assert p is None and t['paper_id']=='' and t['taxonomy_id']=='doi:10.1109/tmm.2023.3313503'
        else:assert p['research_types']==TYPES[rid]
    elif rid=='P231':
        assert p['venue_track']=='Main' and p['venue_id']=='venue:mad'
        assert p['venue_name']=='ACM International Workshop on Multimedia AI against Disinformation'
        assert f'[venue-state:{confirmation_fingerprint(p)}]' in d['review_note']
        assert 'not an official quoted MAD designation' in d['review_note']
        assert 'does not assert ICMR main-conference publication' in d['review_note']
        assert t==binding['before_authoritative_state']['taxonomy']
        aliases=csv_rows(current('data/curated/venue_aliases.csv'))
        audited,issue=VenueAudit(aliases,decisions=[d]).paper(p)
        assert issue is None and audited['venue_id']=='venue:mad' and audited['venue_track']=='Main'
        assert audited['venue_label']=='ACM International Workshop on Multimedia AI against Disinformation (MAD)'
    else:
        assert case['disposition']==binding['disposition']==('IDENTITY_BLOCKED' if rid=='R154' else 'EVIDENCE_INSUFFICIENT')
        assert binding['accepted_changes'] is None
        assert t==binding['before_authoritative_state']['taxonomy']
        before=deepcopy(binding['before_authoritative_state']['paper'])
        # R231's independent research question remains held; the separately
        # accepted P231 action is the sole permitted same-paper track change.
        if rid=='R231':before['venue_track']='Main'
        assert p==before
    return True


def test_original_scope_and_exact_portable_evidence_seals():
    assert len(CASES)==11 and len({r['paper_id'] for r in CASES.values()})==10
    assert set(CASES)==ACCEPTED|HOLDS==set(EVIDENCE)
    assert M['baseline_commit']==BASE==MATRIX['baseline_commit']
    assert sha((O/'adjudication_manifest.json').read_bytes())=='189eabed6bfd3989ceb1abc8300c7b80e12e4453cb13e1fa4397e72b6cd753f0'
    portable=json.loads((ARCHIVE/'portable_evidence_manifest.json').read_text())
    # This is explicitly a partial archive: no omitted manuscript is silently
    # represented as bundled evidence, and original seal bytes remain intact.
    assert portable['partial_archive'] is True
    assert portable['original_external_archives_unchanged'] is True
    assert len(portable['entries'])==113
    paths=[e['repository_path'] for e in portable['entries']]
    assert len(paths)==len(set(paths))
    for entry in portable['entries']:
        raw=(R/entry['repository_path']).read_bytes()
        assert sha(raw)==entry['sha256'] and len(raw)==entry['bytes']
    seal=json.loads((B/'checksums.json').read_text())
    assert len(seal['files'])==123
    assert sha((B/'checksums.json').read_bytes())==M['B3_checksums_sha256']
    assert sha((B/'completion.json').read_bytes())==M['B3_completion_sha256']
    assert sha((B/'batch_dispositions.json').read_bytes())==M['B3_matrix_sha256']
    for path in ['batch_dispositions.json',*(f'per_paper/{rid}.json' for rid in CASES)]:
        expected=seal['files'][path]
        assert sha((B/path).read_bytes())==(expected['sha256'] if isinstance(expected,dict) else expected)


@pytest.mark.parametrize('rid',sorted(CASES))
def test_each_action_acceptance_or_open_hold(rid):
    live=[d for d in read_review_decisions(R/D) if d['decision_id']==CASES[rid]['native_id']]
    assert len(live)==1
    assert valid_case(CASES[rid],decision=live[0])


def test_raw_prefix_and_every_actual_cell_delta():
    before,after=csv_rows(old(D)),csv_rows(current(D))
    assert sha(old(D))=='3430814d49d8e73a5836c71fb04b5acb3e95de3dac56bb795ca62dcf734bfda5'
    assert len(before)==127 and len(after)==138 and current(D).startswith(old(D))
    assert after[:127]==before and after[127:]==[r['formal_decision'] for r in M['records']]
    assert len({r['decision_id'] for r in after})==138
    deltas=[]
    for path,key in [(P,'paper_id'),(T,'taxonomy_id')]:
        a,b=csv_rows(old(path)),csv_rows(current(path))
        assert len(a)==len(b) and [r[key] for r in a]==[r[key] for r in b]
        assert old(path).count(b'\r\n')==current(path).count(b'\r\n')==16
        for x,y in zip(a,b):
            deltas.extend({'path':path,'key_field':key,'key':x[key],'field':k,'before':x[k],'after':y[k]} for k in x if x[k]!=y[k])
    sort=lambda ds:sorted(ds,key=lambda d:(d['path'],d['key'],d['field']))
    assert len(deltas)==35 and sort(deltas)==sort(M['cell_deltas'])
    assert Counter(d['field'] for d in deltas)=={'research_types':9,'research_types_review_reason':5,
           'research_types_evidence_tier':5,'research_types_evidence_source':5,
           'research_types_evidence_excerpt':5,'audited_at':5,'venue_track':1}


def test_authoritative_public_taxonomy_totals_match_exact_approved_evolution():
    registry=read_paper_taxonomy_registry(R/T)
    assert len(registry)==722
    before=published_context(BASE);now=load_context(R)
    assert now['counts']==before['counts']==M['public_counts_unchanged']
    assert now['counts']=={'public':674,'formal':557,'mapped':613,'unmapped':61,'relationship_rows':1410,'unique_paper_institution_pairs':1410}
    assert now['pairs']==before['pairs']
    totals=lambda ctx:dict(Counter(label for row in ctx['taxonomy'].values() for label in row['research_types'].split(';') if label))
    tasktotals=lambda ctx:dict(Counter(label for row in ctx['taxonomy'].values() for label in row['tasks'].split(';') if label))
    assert totals(before)==M['taxonomy_before']['research_types']
    assert totals(now)==M['taxonomy_after']['research_types']=={'method':578,'dataset':142,'benchmark':101,'survey':21,'analysis_study':86}
    assert tasktotals(now)==tasktotals(before)=={'detection':621,'source_attribution':84,'localization':45}
    assert Counter(totals(now))-Counter(totals(before))=={'dataset':4,'benchmark':4}
    public=Counter(label for p in now['papers'].values() for label in p['tasks']+p['research_types'])
    assert public=={**tasktotals(now),**totals(now)}
    for pid,paper in now['papers'].items():
        assert paper['tasks']==before['papers'][pid]['tasks']
        for field in ('title','authors','year','doi','arxiv_id','openalex_url','paper_id','publication_type',
                      'paper_url','url','formal_url','arxiv_url','primary_url','landing_page_url','image_scopes'):
            assert paper.get(field)==before['papers'][pid].get(field),(pid,field)


def test_accounting_independent_original_ledger():
    ledger=[r for r in decision_rows(load_queues(R)) if r['batch']=='B']
    assert len(ledger)==159 and len({r['paper_id'] for r in ledger})==148
    public=load_context(R)['papers']
    legacy={'review:b9f458d69de24b8aae0a':'R267','review:aa32e93a24ade10ed99d':'R236'}
    def count(raw):
        closed=[]
        for d in csv_rows(raw):
            if d['action']!='no_action_after_review':continue
            m=re.search(r'\bBatch B review ([A-Z]\d{3});',d['review_note'])
            rid=m[1] if m else legacy.get(d['decision_id'])
            if rid:closed.append(rid)
        assert len(closed)==len(set(closed))
        pending=[r for r in ledger if r['review_id'] not in closed]
        active=[r for r in pending if r['paper_id'] in public]
        result={'original_actions':159,'original_papers':148,'terminal_actions':len(closed),
                'historical_unresolved_actions':len(pending),'historical_unresolved_papers':len({r['paper_id'] for r in pending}),
                'active_public_unresolved_actions':len(active),'active_public_unresolved_papers':len({r['paper_id'] for r in active})}
        return result,set(closed)
    a,closed_before=count(old(D));b,closed_after=count(current(D))
    assert a==M['accounting_before'] and b==M['accounting_after']
    assert closed_after-closed_before==ACCEPTED and not HOLDS&closed_after
    assert (b['historical_unresolved_actions'],b['active_public_unresolved_actions'])==(114,112)
    assert (b['historical_unresolved_papers'],b['active_public_unresolved_papers'])==(108,106)
    assert 'P231' in closed_after and 'R231' not in closed_after


@pytest.mark.parametrize('rid',sorted(CASES))
def test_native_helper_double_submission_is_byte_and_timestamp_idempotent(rid,tmp_path):
    p=tmp_path/'decisions.csv';p.write_bytes(current(D));expected=p.read_bytes()
    d=CASES[rid]['formal_decision']
    assert upsert_review_decision(d,p)==d
    assert upsert_review_decision(d,p)==d
    assert p.read_bytes()==expected and len(read_review_decisions(p))==138


@pytest.mark.parametrize('rid',sorted(CASES))
@pytest.mark.parametrize('damage',['id','action','queue','creator','identity','note','matrix_hash','record_hash','binding_hash','question','provenance','acceptance'])
def test_acceptance_rejects_wrong_identity_provenance_and_authorization(rid,damage):
    c=deepcopy(CASES[rid]);d=c['formal_decision']
    if damage=='id':d['decision_id']='review:00000000000000000000'
    elif damage=='action':d['action']='unresolved' if d['action']=='no_action_after_review' else 'no_action_after_review'
    elif damage=='queue':d['review_queue']='institutions'
    elif damage=='creator':d['created_by']='local_admin'
    elif damage=='identity':d['doi']='10.0000/different'
    elif damage=='note':d['review_note']='Batch B review '+rid+'; unsupported'
    elif damage=='matrix_hash':c['binding']['B3_matrix_sha256']='0'*64
    elif damage=='record_hash':c['binding']['B3_record_sha256']='0'*64
    elif damage=='binding_hash':c['binding_sha256']='0'*64
    elif damage=='question':c['binding']['original_question']['review_id']='R999'
    elif damage=='provenance':c['source_provenance']=[]
    elif damage=='acceptance':c['accepted']=not c['accepted']
    with pytest.raises(AssertionError):valid_case(c)


@pytest.mark.parametrize('rid',sorted(TYPES))
@pytest.mark.parametrize('field,value',[('research_types','method;survey'),('research_types_evidence_tier','abstract'),('research_types_evidence_source',''),('research_types_evidence_excerpt','')])
def test_reject_unsupported_resource_state(rid,field,value):
    c=CASES[rid];t=deepcopy(maps(T,'taxonomy_id')[c['taxonomy_id']]);t[field]=value
    with pytest.raises(AssertionError):valid_case(c,taxonomy=t)


@pytest.mark.parametrize('field,value',[('venue_id','venue:icmr'),('venue_name','ICMR'),('venue_track','Workshop')])
def test_reject_unfaithful_P231_state(field,value):
    c=CASES['P231'];p=deepcopy(maps(P,'paper_id')[c['paper_id']]);p[field]=value
    with pytest.raises(AssertionError):valid_case(c,paper=p)


def test_required_caveats_are_preserved_separately_from_acceptance():
    assert 'video-derived frames' in CASES['R171']['formal_decision']['review_note']
    assert 'global 1:1:1 balance is arithmetically possible' in CASES['R256']['formal_decision']['review_note']
    assert 'generated-only' in CASES['R275']['formal_decision']['review_note']
    assert CASES['R154']['scientific_limitations']==EVIDENCE['R154']['limitations']
    assert len({c['binding_sha256'] for c in CASES.values()})==11
    assert CASES['R231']['binding_sha256']!=CASES['P231']['binding_sha256']


def test_only_approved_authoritative_files_and_exact_source_bytes_change():
    allowed={P,T,D}
    generated={'data/manual/key_paper_coverage_report.csv','data/manual/missing_author_mappings_report.csv'}
    paths=subprocess.check_output(['git','--no-optional-locks','ls-tree','-r','--name-only',BASE,'--','data/curated','data/manual'],cwd=R,text=True).splitlines()
    for path in paths:
        if path not in allowed|generated:
            assert current(path)==old(path),path
    for path,digest in M['source_before_sha256'].items():
        assert sha(old(path))==digest
    for path,digest in M['source_after_sha256'].items():
        assert sha(current(path))==digest
    assert json.loads((O/'b5_02_handoff.json').read_text())['baseline_commit']==BASE


def expected_public_projection(before, rid, *, marker=False):
    """Explicit authorized fields, independently of the export implementation.

    Neither a large experimental pool nor a venue name alone authorizes these
    projections. The five resource additions and the qualified track are tied
    to the exact source transaction above. Everything else stays byte-logical.
    """
    expected=deepcopy(before)
    if rid in TYPES:
        tax=maps(T,'taxonomy_id')[CASES[rid]['taxonomy_id']]
        expected['research_types']=TYPES[rid].split(';')
        expected['taxonomy_review']['research_types']['reason']=tax['research_types_review_reason']
    elif rid=='P231':
        expected['venue_track']='Main'
        expected['venue_review_required']=False
        expected.pop('venue_review_reason',None)
        expected['metadata_status']['field_overrides'].pop('venue')
        # Fresh curated markers have no ambiguity_status field; the canonical
        # paper retains its historical value. Preserve that schema distinction.
        if marker:
            expected.pop('ambiguity_status',None)
    return expected


def public_paper_ids_for_maps(records):
    from scripts.curated_export import PaperIdentityCache, PaperIdentityIndex
    index=PaperIdentityIndex(csv_rows(old(T)),PaperIdentityCache())
    aliases=published_context(BASE)['taxonomy_to_public_id']
    result={}
    for mid,row in records.items():
        matched=index.matches(row)
        assert len(matched)==1,(mid,'unresolved map identity')
        result[mid]=aliases[matched[0]['taxonomy_id']]
    return result


def assert_public_transaction(papers, markers):
    before=published_context(BASE)['papers']
    old_maps={row['id']:row for row in json.loads(old('web/data/public_preview_map_data.json'))['records']}
    assert papers.keys()==before.keys()
    assert markers.keys()==old_maps.keys()
    inverse={CASES[rid]['paper_id']:rid for rid in ACCEPTED}
    changed={pid for pid in papers if papers[pid]!=before[pid]}
    assert changed==set(inverse)
    for pid,paper in papers.items():
        rid=inverse.get(pid)
        assert paper==expected_public_projection(before[pid],rid),(pid,'unapproved public projection')
    identities=public_paper_ids_for_maps(old_maps)
    dependents={mid for mid,pid in identities.items() if pid in inverse}
    assert {mid for mid in markers if markers[mid]!=old_maps[mid]}==dependents
    assert len(dependents)==14
    for mid,row in markers.items():
        rid=inverse.get(identities[mid])
        assert row==expected_public_projection(old_maps[mid],rid,marker=True),(mid,'unapproved map projection')


def test_public_projection_updates_exactly_six_papers_and_fourteen_dependents():
    papers=load_context(R)['papers']
    markers={row['id']:row for row in json.loads(current('web/data/public_preview_map_data.json'))['records']}
    assert_public_transaction(papers,markers)
    paper=papers[CASES['P231']['paper_id']]
    assert paper['venue_id']=='venue:mad'
    assert paper['venue_name']=='ACM International Workshop on Multimedia AI against Disinformation'
    assert paper['venue_label']=='ACM International Workshop on Multimedia AI against Disinformation (MAD)'
    assert 'Main' not in paper['venue_label'] and 'ICMR' not in paper['venue_label']
    assert paper['research_types']==['method']


@pytest.mark.parametrize('damage',['unrelated_type','identity','author','publication_link','map_location',
                                   'map_identity','map_type','mad_identity','missing_resource','fake_benchmark',
                                   'marker_ambiguity_insertion','paper_ambiguity_removal'])
def test_public_projection_rejects_unapproved_or_incomplete_changes(damage):
    old_papers=published_context(BASE)['papers']
    old_maps={row['id']:row for row in json.loads(old('web/data/public_preview_map_data.json'))['records']}
    inverse={CASES[rid]['paper_id']:rid for rid in ACCEPTED}
    papers={pid:expected_public_projection(row,inverse.get(pid)) for pid,row in old_papers.items()}
    identities=public_paper_ids_for_maps(old_maps)
    markers={mid:expected_public_projection(row,inverse.get(identities[mid]),marker=True) for mid,row in old_maps.items()}
    unrelated=next(pid for pid in papers if pid not in inverse)
    mid=next(iter(markers))
    if damage=='unrelated_type':papers[unrelated]['research_types'].append('benchmark')
    elif damage=='identity':papers[unrelated]['doi']='10.0000/unrelated'
    elif damage=='author':papers[unrelated]['authors']=[]
    elif damage=='publication_link':papers[unrelated]['formal_url']='https://invalid.example/'
    elif damage=='map_location':markers[mid]['lat']=0
    elif damage=='map_identity':markers[mid]['institution_id']='institution:unrelated'
    elif damage=='map_type':markers[mid]['tasks']=['source_attribution']
    elif damage=='mad_identity':papers[CASES['P231']['paper_id']]['venue_id']='venue:icmr'
    elif damage=='missing_resource':papers[CASES['R110']['paper_id']]['research_types']=['method']
    elif damage=='fake_benchmark':papers[CASES['R564']['paper_id']]['research_types'].append('benchmark')
    elif damage=='marker_ambiguity_insertion':
        target=next(mid for mid,pid in identities.items() if pid==CASES['P231']['paper_id'])
        markers[target]['ambiguity_status']='unresolved'
    elif damage=='paper_ambiguity_removal':papers[CASES['P231']['paper_id']].pop('ambiguity_status')
    with pytest.raises(AssertionError):assert_public_transaction(papers,markers)


def test_paired_export_metadata_preserves_every_nontimestamp_field():
    from scripts.public_export_metadata import is_utc_timestamp
    times=[]
    for path in ('web/data/public_preview_papers.json','web/data/public_preview_map_data.json'):
        before,after=json.loads(old(path)),json.loads(current(path))
        old_metadata,new_metadata=deepcopy(before['metadata']),deepcopy(after['metadata'])
        old_time,new_time=old_metadata.pop('public_preview_generated_at'),new_metadata.pop('public_preview_generated_at')
        assert old_metadata==new_metadata
        assert is_utc_timestamp(new_time) and new_time>=old_time
        assert {k:v for k,v in before.items() if k not in {'metadata','records'}}=={k:v for k,v in after.items() if k not in {'metadata','records'}}
        times.append(new_time)
    assert times[0]==times[1]


def test_preserved_caveats_do_not_claim_independently_reproduced_results():
    taxonomy=maps(T,'taxonomy_id')
    excerpts={rid:taxonomy[CASES[rid]['taxonomy_id']]['research_types_evidence_excerpt'] for rid in TYPES}
    assert 'video-derived frames' in excerpts['R171'] and 'static-image' in excerpts['R171']
    assert 'global 1:1:1 balance is arithmetically possible' in excerpts['R256']
    assert 'unspecified, not disproved' in excerpts['R256']
    assert 'generated-only' in excerpts['R275'] and 'not balanced real/fake accuracy or specificity' in excerpts['R275']
    assert 'R1 dataset label is not added' in excerpts['R275']
    assert all(case['empirical_results_independently_reproduced'] is False for case in CASES.values())
    assert CASES['R231']['accepted'] is False and CASES['P231']['accepted'] is True
    assert 'Main is not an official quoted MAD designation' in M['P231_semantic_qualification']

def test_generated_mapping_and_coverage_csvs_have_no_unrelated_changes():
    for path in ('data/manual/missing_author_mappings_report.csv','data/manual/key_paper_coverage_report.csv'):
        assert current(path)==old(path),path


def test_no_website_or_institution_source_changes_outside_paired_exports():
    paths=subprocess.check_output(['git','--no-optional-locks','ls-tree','-r','--name-only',BASE,'--','web'],cwd=R,text=True).splitlines()
    for path in paths:
        if path not in {'web/data/public_preview_papers.json','web/data/public_preview_map_data.json'}:
            assert current(path)==old(path),path
    frozen=json.loads(current('data/raw/systematic_gap_migration_2026_10_03/baseline.json'))['frozen_sha256']
    assert len(frozen)==49
    from scripts.literature51_reproducibility import preserved_bytes
    for path,digest in frozen.items():
        assert sha(preserved_bytes(R,path))==digest,path

def assert_source_transaction(raw_by_path):
    """Reject any edit outside the exact independently approved source bytes.

    A historical snapshot passing its own hashes never grants permission to
    modify current files. This gate authenticates the separately accepted B4-03
    transaction and preserves the complete 127-row published prefix.
    """
    assert set(raw_by_path)=={P,T,D}
    assert sha((O/'adjudication_manifest.json').read_bytes())=='189eabed6bfd3989ceb1abc8300c7b80e12e4453cb13e1fa4397e72b6cd753f0'
    for path,raw in raw_by_path.items():
        assert sha(raw)==M['source_after_sha256'][path],path
    before=old(D)
    assert raw_by_path[D].startswith(before)
    rows=csv_rows(raw_by_path[D])
    assert len(rows)==len({row['decision_id'] for row in rows})==138
    assert rows[:127]==csv_rows(before)
    assert rows[127:]==[case['formal_decision'] for case in M['records']]


def test_current_source_has_an_independent_exact_transaction_guard():
    assert_source_transaction({path:current(path) for path in (P,T,D)})


@pytest.mark.parametrize('damage',['predecessor_decision','successor_decision_id','unrelated_task','identity','taxonomy_type'])
def test_current_source_guard_rejects_tampering_independently_of_historical_success(damage):
    raw={path:current(path) for path in (P,T,D)}
    if damage=='predecessor_decision':
        row=csv_rows(old(D))[0]
        key=row['decision_id'].encode()
        assert key in raw[D]
        raw[D]=raw[D].replace(key,b'review:00000000000000000000',1)
    elif damage=='successor_decision_id':
        key=CASES['R110']['native_id'].encode()
        assert key in raw[D]
        raw[D]=raw[D].replace(key,b'review:00000000000000000000',1)
    elif damage=='unrelated_task':
        assert b',detection,' in raw[P]
        raw[P]=raw[P].replace(b',detection,',b',source_attribution,',1)
    elif damage=='identity':
        key=CASES['R110']['paper_id'].encode()
        raw[P]=raw[P].replace(key,b'curated:unrelated',1)
    else:
        assert b'method;dataset;benchmark' in raw[T]
        raw[T]=raw[T].replace(b'method;dataset;benchmark',b'method;survey',1)
    with pytest.raises(AssertionError):assert_source_transaction(raw)
