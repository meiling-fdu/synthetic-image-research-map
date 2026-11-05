"""Current B4-04 source endpoint, independently of immutable historical replays."""
from copy import deepcopy
from pathlib import Path
import csv,gzip,hashlib,io,json,re,subprocess,sys
from unittest.mock import patch
import pytest

R=Path(__file__).resolve().parents[1]
O=R/'tests/fixtures/batch_b_b4_04'
B=O/'b3_04'
BASE='2932b9a5b58a8c84761e381668925a765ca9719e'
P='data/curated/papers.csv';T='data/curated/paper_taxonomy.csv';D='data/curated/review_decisions.csv'
TARGETS={'R124':'method;dataset;benchmark','R149':'method;dataset','R223':'method;dataset','R363':'method;dataset',
         'R477':'dataset;analysis_study','R509':'method;analysis_study','R512':'method;dataset;analysis_study','R625':'method;analysis_study'}
HOLDS={'R045','R156','R251','R284','P251'}
sys.dont_write_bytecode=True;sys.path.insert(0,str(R))
from scripts.review_decisions import upsert_review_decision
from scripts.paper_taxonomy_registry import read_paper_taxonomy_registry,public_taxonomy_fields
from scripts.validate_corpus_quality_audit import load_context,load_queues,decision_rows
M=json.loads((O/'adjudication_manifest.json').read_text());CASES={r['review_id']:r for r in M['records']}
E={r['review_id']:r for r in json.loads((B/'batch_dispositions.json').read_text())['records']}
CTX=load_context(R)

def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def old(p):return subprocess.check_output(['git','--no-optional-locks','show',BASE+':'+p],cwd=R)
def rows(b):return list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'),newline='')))
def maps(p,key):return {r[key]:r for r in rows((R/p).read_bytes())}
def native(d):return 'review:'+sha('|'.join(' '.join(str(d.get(k) or '').split()).casefold() for k in ['review_queue','target_type','doi','openalex_url','title','year','institution']).encode())[:20]

def accepted_case(c):
 rid=c['review_id'];e=E[rid];b=c['binding'];d=c['formal_decision']
 ledger={r['review_id']:r for r in decision_rows(load_queues(R)) if r['batch']=='B'}
 assert rid in set(TARGETS)|HOLDS and b['original_question']==ledger[rid]
 assert b['baseline_commit']==BASE and b['review_id']==rid and b['paper_id']==e['paper_id']==c['paper_id']
 assert b['B3_matrix_sha256']==sha((B/'batch_dispositions.json').read_bytes())=='2940a50d236c346af9bd3e4335b3a40c7bb4e71c2b935096daafc01a97c96c43'
 assert b['B3_record_path']==e['evidence_record'] and b['B3_record_sha256']==e['evidence_record_sha256']==sha((B/e['evidence_record']).read_bytes())
 assert b['source_provenance']==c['source_provenance']==e['source_provenance']
 assert b['limitations']==c['scientific_limitations']==e['limitations']
 assert b['B3_QC']==e['independent_QC'] and b['policies']==e['governing_policy_ids']
 assert sha(canonical(b))==c['binding_sha256'] and f'[b4-04-state:{c["binding_sha256"]}]' in d['review_note']
 assert c['action_fingerprint']==sha(canonical({'review_id':rid,'original_question':ledger[rid]}))
 assert f'[action:{c["action_fingerprint"]}]' in d['review_note'] and d['review_note'].startswith(f'Batch B review {rid};')
 assert d['decision_id']==c['native_id']==native(d)
 for field in ['title','year','doi','openalex_url']:
  assert d[field]==str(b['canonical_bibliographic_identity'].get(field) or '')==str(CTX['papers'][c['paper_id']].get(field) or '')
 assert b['canonical_bibliographic_identity']['authors']==CTX['papers'][c['paper_id']]['authors']
 assert d['review_queue']==('publication_venues' if rid=='P251' else 'other') and d['target_type']=='paper' and not d['institution']
 assert d['created_by']=='maintainer-approved-batch-b-b4-04' and d['created_at']==d['updated_at']
 assert c['accepted']==b['accepted']==(rid in TARGETS) and c['empirical_results_independently_reproduced'] is False
 assert d['action']==('no_action_after_review' if rid in TARGETS else 'unresolved')
 t=maps(T,'taxonomy_id')[c['taxonomy_id']];p=maps(P,'paper_id').get(c['paper_id'])
 if rid in TARGETS:
  assert t['research_types']==p['research_types']==TARGETS[rid]
  assert t['research_types_evidence_tier']=='primary_paper' and t['audited_at']=='2026-11-03'
  for field in ['research_types_review_reason','research_types_evidence_source','research_types_evidence_excerpt']:
   assert t[field] and t[field]==b['expected_after_state']['taxonomy'][field]
  assert b['accepted_changes'] and not c['removed_labels']
 else:
  assert b['accepted_changes'] is None and t==b['before_authoritative_state']['taxonomy'] and p==b['before_authoritative_state']['paper']
  assert c['disposition']==('AUTHORITATIVE_WRITE_PATH_BLOCKED' if rid=='P251' else 'EVIDENCE_INSUFFICIENT')
 return True

@pytest.mark.parametrize('rid',list(CASES))
def test_each_formal_outcome_has_exact_identity_evidence_policy_and_current_state(rid):assert accepted_case(CASES[rid])

def test_exact_source_delta_and_prior138_raw_prefix():
 reviewraw=gzip.decompress((O/'qc/independent_preapply_review.json.gz').read_bytes())
 assert sha(reviewraw)=='08f5ba0b909bdf3933a03b98fcd9e0a6eee91c782d97ff9c75d14ee5bb027cd1'
 review=json.loads(reviewraw)
 assert review['status']=='PASS' and review['manifest_sha256']==sha((O/'adjudication_manifest.json').read_bytes())
 assert set(CASES)==set(TARGETS)|HOLDS and len(CASES)==13 and len({c['paper_id'] for c in CASES.values()})==12
 expected=[]
 for rid in TARGETS:expected+=CASES[rid]['binding']['accepted_changes']
 actual=[]
 for path,key in [(P,'paper_id'),(T,'taxonomy_id')]:
  before=rows(old(path));now=rows((R/path).read_bytes());assert [r[key] for r in before]==[r[key] for r in now]
  for a,b in zip(before,now):
   actual += [{'path':path,'key_field':key,'key':a[key],'field':k,'before':a[k],'after':b[k]} for k in a if a[k]!=b[k]]
 assert sorted(actual,key=canonical)==sorted(expected,key=canonical)==sorted(M['cell_deltas'],key=canonical)
 assert {x['field'] for x in actual if x['path']==T}<={'research_types','research_types_review_reason','research_types_evidence_tier','research_types_evidence_source','research_types_evidence_excerpt','audited_at'}
 assert {x['field'] for x in actual if x['path']==P}=={'research_types'}
 for path in [P,T]:assert (R/path).read_bytes().count(b'\r\n')==old(path).count(b'\r\n')
 previous=old(D);now=(R/D).read_bytes();assert now.startswith(previous) and len(rows(previous))==138
 dr=rows(now);assert len(dr)==len({r['decision_id'] for r in dr})==151
 assert dr[138:]==[c['formal_decision'] for c in M['records']]
 assert len({c['native_id'] for c in CASES.values()})==len({c['action_fingerprint'] for c in CASES.values()})==13

def test_recomputed_source_totals_and_unchanged_public_identities_and_relationships():
 ctx=load_context(R);assert ctx['counts']==M['public_invariants']=={'public':674,'formal':557,'mapped':613,'unmapped':61,'relationship_rows':1410,'unique_paper_institution_pairs':1410}
 from collections import Counter
 current=Counter(x for r in ctx['taxonomy'].values() for x in r['research_types'].split(';') if x)
 assert dict(current)==M['taxonomy_after']['research_types']
 before=Counter(M['taxonomy_before']['research_types']);assert current-before=={'dataset':4,'benchmark':1,'analysis_study':4} and not before-current
 assert M['taxonomy_after']['tasks']==M['taxonomy_before']['tasks']=={'detection':621,'source_attribution':84,'localization':45}
 for path in ['web/data/public_preview_papers.json','web/data/public_preview_map_data.json']:assert (R/path).read_bytes()==old(path)
 for rid in TARGETS:
  c=CASES[rid];p=ctx['papers'][c['paper_id']];projected=public_taxonomy_fields(ctx['taxonomy'][c['paper_id']])
  assert projected['research_types']==TARGETS[rid].split(';') and projected['tasks']==p['tasks']

def test_accounting_closes_only_eight_taxonomy_questions():
 legacy={'review:b9f458d69de24b8aae0a':'R267','review:aa32e93a24ade10ed99d':'R236'}
 def closed(raw):
  values=[]
  for d in rows(raw):
   if d['action']!='no_action_after_review':continue
   m=re.search(r'\bBatch B review ([A-Z]\d{3});',d['review_note']);rid=m[1] if m else legacy.get(d['decision_id'])
   if rid:values.append(rid)
  assert len(values)==len(set(values));return set(values)
 before=closed(old(D));after=closed((R/D).read_bytes());assert after-before==set(TARGETS) and not after&HOLDS
 ledger=[r for r in decision_rows(load_queues(R)) if r['batch']=='B'];public=load_context(R)['papers']
 pending=[r for r in ledger if r['review_id'] not in after];active=[r for r in pending if r['paper_id'] in public]
 assert len(ledger)==159 and len(pending)==M['accounting_after']['historical_unresolved']==106
 assert len(active)==M['accounting_after']['active_public_unresolved']==104

@pytest.mark.parametrize('rid',list(CASES))
def test_real_native_helper_repeated_submission_is_byte_timestamp_idempotent(rid,tmp_path):
 p=tmp_path/'review_decisions.csv';p.write_bytes((R/D).read_bytes());before=p.read_bytes();d=CASES[rid]['formal_decision']
 with patch('scripts.review_decisions._now',return_value='2026-11-04T00:00:00Z'):
  assert upsert_review_decision(d,p)==d and upsert_review_decision(d,p)==d
 assert p.read_bytes()==before

@pytest.mark.parametrize('rid',list(CASES))
@pytest.mark.parametrize('damage',['id','action','queue','creator','identity','binding_hash','original_question','evidence_hash','source','policy','acceptance'])
def test_rejects_tampered_decision_identity_evidence_and_authorization(rid,damage):
 c=deepcopy(CASES[rid]);d=c['formal_decision'];b=c['binding']
 if damage=='id':d['decision_id']='review:unreviewed'
 elif damage=='action':d['action']='unresolved' if d['action']=='no_action_after_review' else 'no_action_after_review'
 elif damage=='queue':d['review_queue']='manual_import'
 elif damage=='creator':d['created_by']='unreviewed'
 elif damage=='identity':b['paper_id']='curated:unrelated'
 elif damage=='binding_hash':c['binding_sha256']='0'*64
 elif damage=='original_question':b['original_question']['reason']='unrelated question'
 elif damage=='evidence_hash':b['B3_record_sha256']='0'*64
 elif damage=='source':b['source_provenance'][0]['url']='https://example.invalid/unreviewed'
 elif damage=='policy':b['policies']=['UNREVIEWED_POLICY']
 elif damage=='acceptance':c['accepted']=not c['accepted']
 with pytest.raises(AssertionError):accepted_case(c)

def test_P251_paper_author_and_schema_hold_is_exactly_preserved():
 c=CASES['P251'];assessment=json.loads((O/'investigation/P251_write_path_assessment.json').read_text())
 assert assessment['recommendation']=='HOLD' and not assessment['safe_existing_authoritative_write_path']
 assert c['binding']['before_authoritative_state']['paper'] is None
 assert c['binding']['canonical_bibliographic_identity']['authors'][0]['name']=='Jefferson Ng'
 assert 'Jia Chyi Ng' in c['formal_decision']['review_note'] and 'not a verified Jefferson Ng personal alias' in c['formal_decision']['review_note']
 assert c['disposition']=='AUTHORITATIVE_WRITE_PATH_BLOCKED' and CASES['R251']['disposition']=='EVIDENCE_INSUFFICIENT'
 assert c['native_id']!=CASES['R251']['native_id'] and c['action_fingerprint']!=CASES['R251']['action_fingerprint']

def test_R512_conditional_prevalence_and_other_required_caveats():
 t=maps(T,'taxonomy_id')[CASES['R512']['taxonomy_id']]['research_types_evidence_excerpt']
 assert all(x in t for x in ['80.71%','83.33%','five-fake/one-real','IF','not verified publisher-final'])
 assert maps(T,'taxonomy_id')[CASES['R477']['taxonomy_id']]['research_types']=='dataset;analysis_study'
 assert CASES['R156']['binding']['accepted_changes'] is None and 'Original NOT_SUPPORTED' in CASES['R156']['formal_decision']['review_note']

def test_all_other_curated_manual_raw_and_website_paths_unchanged():
 names=subprocess.check_output(['git','--no-optional-locks','ls-tree','-r','--name-only',BASE],cwd=R).decode().splitlines()
 for path in names:
  if path.startswith(('data/','web/')) and path not in [P,T,D]:assert (R/path).read_bytes()==old(path),path
 assert not subprocess.check_output(['git','--no-optional-locks','diff','--cached','--name-only'],cwd=R)
