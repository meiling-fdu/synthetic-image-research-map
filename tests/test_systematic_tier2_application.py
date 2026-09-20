"""Approved narrowed scope: application-only invariants and regression cases."""
import copy
import csv
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('tier2_application',ROOT/'scripts/report_systematic_tier2_application.py')
p=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(p)


def indexed():
    return {r['candidate_id']:r for r in p.inputs()[0]}


def test_exact_population_and_unchanged_cluster_join():
    rows,legacy=p.inputs()
    p.validate(rows,legacy)
    assert len(rows)==215
    assert {r['primary_policy_cluster'] for r in rows}==set(p.CLUSTERS)


def test_foreign_or_duplicate_candidate_rejected():
    rows,legacy=p.inputs()
    broken=copy.deepcopy(rows);broken[-1]=broken[0]
    with pytest.raises(AssertionError):p.validate(broken,legacy)
    broken=copy.deepcopy(rows);broken[0]['candidate_id']='not-a-tier2-candidate'
    with pytest.raises(AssertionError):p.validate(broken,legacy)


def test_no_unresolved_user_policy_or_corpus_action_outcomes():
    rows,legacy=p.inputs()
    assert all(r['policy_outcome'] in p.OUTCOMES for r in rows)
    for bad in ['USER_POLICY_DECISION_REQUIRED','MISSING_ADD','OUT_OF_SCOPE']:
        broken=copy.deepcopy(rows);broken[0]['policy_outcome']=bad
        with pytest.raises(AssertionError):p.validate(broken,legacy)


def test_watermark_mechanisms_default_exclude_with_explicit_exception_check():
    rows,legacy=p.inputs()
    wm=[r for r in rows if r['primary_policy_cluster'] in {'EMBED','VERIFY','WM_EVAL','HYBRID'}]
    review=[r for r in wm if r['policy_outcome']!='POLICY_EXCLUDE']
    assert [r['candidate_id'] for r in review]==['audit:cf16307ced603a1d']
    assert review[0]['policy_outcome']=='PAPER_SPECIFIC_EVIDENCE_REQUIRED'
    assert 'without SynthID' in review[0]['evidence_review_question']
    broken=copy.deepcopy(rows)
    r=next(r for r in broken if r['primary_policy_cluster']=='EMBED')
    r.update(policy_outcome='POLICY_INCLUDE',primary_exclusion_reason='',mechanism_assessment='PASSIVE')
    with pytest.raises(AssertionError):p.validate(broken,legacy)


def test_face_only_does_not_qualify_through_diffusion_or_localization():
    rows=indexed()
    for id in ['audit:2dd12a0cda658ec2','audit:352f2fb6357d70b7','audit:c4687c6fc6bc7f18']:
        assert rows[id]['policy_outcome']=='POLICY_EXCLUDE'
        assert rows[id]['primary_exclusion_reason']=='PURE_DEEPFAKE_FACE_ONLY'
    broader=rows['audit:0b72dded38f87a65']
    assert broader['policy_outcome']=='PAPER_SPECIFIC_EVIDENCE_REQUIRED'
    assert 'AIGC benchmark' in broader['evidence_review_question']


def test_generative_edit_localization_survives_narrowing():
    rows=indexed()
    for id in ['audit:07194f58b4540acc','audit:3e3ef129a9a7d54a','audit:6bf3721fdb65fc44']:
        assert rows[id]['policy_outcome']=='POLICY_INCLUDE'
    # Diffusion used to generate a detector's mask does not establish input provenance.
    assert rows['audit:bcd4cedccc0c34eb']['policy_outcome']=='PAPER_SPECIFIC_EVIDENCE_REQUIRED'


def test_passive_traces_and_active_injection_are_distinct():
    rows=indexed()
    assert rows['audit:80dc647f134b129b']['policy_outcome']=='POLICY_INCLUDE'
    assert rows['audit:e2e46a2b74be26a6']['primary_exclusion_reason']=='WATERMARK_ACTIVE_PROVENANCE'
    assert rows['audit:2ec9b9251586d3bb']['policy_outcome']=='POLICY_INCLUDE'
    assert rows['audit:5413d2706f713d11']['policy_outcome']=='POLICY_INCLUDE'
    # Improving passive detection through generator intervention is still dependent.
    assert rows['audit:f79b7f4801af24bf']['policy_outcome']=='POLICY_EXCLUDE'


def test_three_queues_partition_and_report_counts_match():
    rows,legacy=p.inputs();artifacts=p.render(rows,legacy);s=json.loads(artifacts['summary.json'])
    ids=[]
    for outcome,name in p.QUEUES.items():
        queue=list(csv.DictReader(io.StringIO(artifacts[name])))
        if outcome == 'POLICY_EXCLUDE':
            assert all(r['policy_outcome']==outcome for r in queue)
        assert len(queue)==s['outcomes'][outcome]
        assert f'| {outcome} | {len(queue)} |' in artifacts[p.REPORT.name]
        ids.extend(r['candidate_id'] for r in queue)
    assert len(ids)==len(set(ids))==215
    assert sum(s['exclusion_reasons'].values())==s['outcomes']['POLICY_EXCLUDE']
    for name,value in artifacts.items():
        canonical=p.REPORT if name==p.REPORT.name else p.OUT/name
        assert canonical.read_text()==value


def test_decision_ready_queue_schemas_and_priorities():
    rows,legacy=p.inputs();artifacts=p.render(rows,legacy)
    include=list(csv.DictReader(io.StringIO(artifacts[p.QUEUES['POLICY_INCLUDE']])))
    evidence=list(csv.DictReader(io.StringIO(artifacts[p.QUEUES['PAPER_SPECIFIC_EVIDENCE_REQUIRED']])))
    assert len(include)==12 and len(evidence)==32
    assert {'title','year','venue','cluster','qualifying_synthetic_image_contribution',
            'proposed_forensic_task','proposed_image_scope','proposed_research_type',
            'saved_evidence','reconciliation_priority'} <= set(include[0])
    assert {'title','cluster','exact_unresolved_question','evidence_already_available',
            'exact_additional_evidence_needed','likely_outcome_if_confirmed',
            'likely_outcome_if_not_confirmed','evidence_review_priority'} <= set(evidence[0])
    assert {r['reconciliation_priority'] for r in include} <= {'HIGH','NORMAL'}
    assert {r['evidence_review_priority'] for r in evidence} == {'HIGH','NORMAL'}
    assert all(r['exact_unresolved_question'].endswith('?') or '?' in r['exact_unresolved_question'] for r in evidence)


def test_legacy_normalization_is_exact_and_separates_broader_work():
    rows,legacy=p.inputs();artifacts=p.render(rows,legacy)
    normalized=list(csv.DictReader(io.StringIO(artifacts['legacy_scope_diagnostic.csv'])))
    s=json.loads(artifacts['summary.json'])
    assert s['legacy_confidence']=={'HIGH':32,'MEDIUM':1,'LOW':43}
    assert s['legacy_disposition']=={
        'LIKELY_PURE_DEEPFAKE':27,
        'LIKELY_SCOPE_DRIFT':5,
        'METADATA_INSUFFICIENT':43,
        'POSSIBLE_BROADER_SYNTHETIC_IMAGE_WORK':1,
    }
    broader=[r for r in normalized if r['diagnostic_disposition']=='POSSIBLE_BROADER_SYNTHETIC_IMAGE_WORK']
    assert len(broader)==1
    assert broader[0]['canonical_title']=='Global Texture Enhancement for Fake Face Detection in the Wild'


def test_evidence_questions_are_specific_and_not_policy_votes():
    rows,legacy=p.inputs()
    for r in rows:
        if r['policy_outcome']=='PAPER_SPECIFIC_EVIDENCE_REQUIRED':
            assert r['evidence_review_question'] and r['manual_review']=='true'
            assert 'user decision' not in r['evidence_review_question'].lower()
    broken=copy.deepcopy(rows)
    next(r for r in broken if r['manual_review']=='true')['evidence_review_question']='scope unclear'
    with pytest.raises(AssertionError):p.validate(broken,legacy)


def test_legacy_is_read_only_and_broader_counterevidence_is_respected():
    rows,legacy=p.inputs();p.validate(rows,legacy)
    titles={r['canonical_title'] for r in legacy}
    assert 'Face X-Ray for More General Face Forgery Detection' in titles
    assert 'OpenFake: An Open Dataset and Platform Toward Real-World Deepfake Detection' not in titles
    assert 'Forging the Unknown: Open-Set Deepfake Attribution via Adaptive Fingerprint Learning' not in titles
    assert all(r['corpus_action']=='NONE' for r in legacy)
    assert any(r['diagnostic_basis']=='deepfake_only_taxonomy_scope_unverified' for r in legacy)


def test_deterministic_generation_cannot_change_manual_or_public_sources(tmp_path):
    files=[p.APPLICATION,p.LEGACY,p.PREVIOUS,p.ORIGINAL,p.PUBLIC]
    before={f:hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    command=[sys.executable,str(ROOT/'scripts/report_systematic_tier2_application.py'),'--output-dir',str(tmp_path)]
    subprocess.run(command,cwd='/tmp',check=True,capture_output=True)
    first={f.name:f.read_bytes() for f in tmp_path.iterdir()}
    subprocess.run(command,cwd='/tmp',check=True,capture_output=True)
    assert first=={f.name:f.read_bytes() for f in tmp_path.iterdir()}
    assert before=={f:hashlib.sha256(f.read_bytes()).hexdigest() for f in files}


def test_pre_application_baseline_includes_and_preserves_previous_policy_pass():
    baseline=json.loads((p.OUT/'baseline_sha256.json').read_text())
    assert 'data/manual/systematic_tier2_scope_policy_clusters_2026_09.csv' in baseline
    assert 'docs/systematic_tier2_scope_policy_review_2026_09.md' in baseline
    assert p.integrity()['changed_paths']==[]
