"""Approved Batch A outcomes and failure cases for scoped affiliation repairs."""
import copy
import json

import pytest

from scripts import validate_corpus_quality_audit as audit
from scripts.corpus_quality_history import predecessor_root, snapshot_bytes
from scripts.remediate_corpus_quality_batch_a import APPROVED, OUT, ROOT
from scripts.export_candidate_map_data import load_institution_author_overrides
from scripts.export_public_preview import add_public_detail_fields, deduplicate_public_map_relationships
from scripts.public_export_guard import analyze_shrinkage
from scripts.migrate_paper_taxonomy import build_registry, write_registry
from scripts.paper_taxonomy_registry import read_paper_taxonomy_registry, apply_paper_taxonomy_registry
from scripts.paper_exclusions import read_exclusion_rows


@pytest.fixture(scope='module')
def state():
    with predecessor_root() as root:
        before=audit.load_context(root)
    actions={r['review_id']:r for r in audit.decision_rows(audit.load_queues()) if r['batch']=='A'}
    return before,audit.load_context(),actions


def batch_a_validation_receipt():
    """Read the immutable Batch A result after later approved successor phases."""
    return json.loads((OUT/'validation.json').read_text())


@pytest.mark.parametrize('review_id', ['T403','T495','T610','R063','R074','R131','R210',
    'R326','R346','R388','R496','R528','R573','R614'])
def test_exact_taxonomy_action(state, review_id):
    before,after,actions=state
    action=actions[review_id];pid=action['paper_id'];dim=action['dimension']
    assert before['papers'][pid][dim]==action['current_labels']
    assert after['papers'][pid][dim]==action['proposed_labels']
    assert after['taxonomy'][pid][dim].split(';')==action['proposed_labels']
    for companion in {'tasks','research_types','image_scopes'}-{dim}:
        assert after['papers'][pid][companion]==before['papers'][pid][companion]


@pytest.mark.parametrize('review_id',['P018','P358','P572'])
def test_formal_version_same_identity_and_author_order(state, review_id):
    before,after,actions=state
    action=actions[review_id];pid=action['paper_id']
    old,new=before['papers'][pid],after['papers'][pid]
    assert old['publication_type']=='preprint'
    assert new['paper_id']==old['paper_id']
    assert new['arxiv_id']==old['arxiv_id']
    assert [a['name'] for a in new['authors']]==[a['name'] for a in old['authors']]
    for key in ('year','doi','publication_type'):
        assert new[key]==action['proposed_changes'][key]
    expected_url=('https://doi.org/'+new['doi']) if new['doi'] else action['proposed_changes']['paper_url']
    assert new['formal_url']==expected_url
    assert new['venue_track']==action['proposed_changes']['venue_track']


def test_lorax_url_only_and_workshop_preserved(state):
    before,after,actions=state
    a=actions['P502'];old=before['papers'][a['paper_id']];new=after['papers'][a['paper_id']]
    assert new['paper_url']==new['formal_url']==a['proposed_changes']['paper_url']
    for field in ('paper_id','arxiv_id','doi','year','venue_id','publication_type','tasks','research_types','authors'):
        assert new.get(field)==old.get(field)
    assert new['venue_track']=='Workshop'


def test_r1_exact_author_groups_and_four_unsupported_links(state):
    before,after,actions=state
    a=actions['L002'];paper=after['papers'][a['paper_id']]
    groups={r['institution_id']:r['authors'] for r in paper['author_institution_affiliations']}
    assert groups==a['proposed_author_groups']
    for link in a['unsupported_links']:
        assert link['author'] not in groups[link['institution_id']]
    assert [a['name'] for a in paper['authors']]==[a['name'] for a in before['papers'][a['paper_id']]['authors']]


def test_r2_natural_exporter_collapse_keeps_r3_pending():
    snapshot=snapshot_bytes()
    old=[r for r in json.loads(snapshot['web/data/public_preview_map_data.json'])['records'] if r.get('arxiv_id')=='2007.10466']
    new=[r for r in json.loads((ROOT/'web/data/public_preview_map_data.json').read_text())['records'] if r.get('arxiv_id')=='2007.10466']
    result=json.loads((OUT/'results.json').read_text())
    groups=next(r['applied_value'] for r in result['records'] if r['review_id']=='L002')
    corrected=[{**r,'institution_authors':groups[r['institution_id']]} for r in old]
    collapsed,removed=deduplicate_public_map_relationships(corrected)
    assert removed==1
    assert len(collapsed)==len(new)==2
    assert result['R3']=='REQUIRES_MAINTAINER_DECISION'
    assert result['UCSB_export_outcome']=='DETERMINISTIC_EXPORT_COLLAPSE_AFTER_R1_R2'
    assert result['manual_R3_merge_applied'] is False
    assert len(next(r['previous_value'] for r in result['records'] if r['review_id']=='L002'))==3
    assert next(r['previous_value'] for r in result['records'] if r['review_id']=='L002')==old
    assert {r['openalex_url'] for r in old}=={'https://openalex.org/W3179128750','https://openalex.org/W3043994911'}


def test_bmvc_registry_reuses_existing_identity_without_duplicate_aliases():
    from scripts.venues import read_venue_aliases
    from scripts.venue_audit import enrich_aliases
    before=snapshot_bytes()['data/curated/venue_aliases.csv']
    import csv
    import io
    historical=list(csv.DictReader(io.StringIO(before.decode())))
    current=read_venue_aliases(include_evidence=False)
    additions=[r for r in current if r not in historical]
    assert len(additions)==1
    row=additions[0]
    assert row['venue_id']=='venue:british-machine-vision-conference'
    assert row['alias']==row['venue_name']=='British Machine Vision Conference'
    assert row['venue_acronym']=='BMVC'
    assert row['venue_track']==''  # Main is confirmed on the paper, not the venue.
    semantic=lambda rows: sorted(tuple(r[k] for k in ('alias','venue_id','venue_name','venue_acronym','venue_type','venue_track','review_status')) for r in enrich_aliases(rows))
    assert semantic(current)==semantic(historical)


def test_all_twenty_results_have_preserved_provenance():
    results=json.loads((OUT/'results.json').read_text())['records']
    assert len(results)==20 and {r['review_id'] for r in results}==APPROVED
    for r in results:
        assert r['status']=='APPLIED'
        assert r['previous_value'] is not None and r['applied_value'] is not None
        assert r['authoritative_evidence'] and r['date'] and r['paper_id']
        assert r['validation_outcome']=='PASS'


def test_exact_scope_integrity_and_remaining_batches():
    result=batch_a_validation_receipt()
    assert result['errors']==[]
    assert result['after']['public']==640
    assert result['after']['formal']==532
    assert result['after']['unmapped']==23
    assert result['remaining_batches']==dict(B=159,C=41,D=1752)
    assert result['relationships_before']['repeated_author_institution_links']==1
    assert result['relationships_after']['repeated_author_institution_links']==0


def test_current_taxonomy_round_trip_preserves_all_rows(tmp_path):
    papers=ROOT/'web/data/public_preview_papers.json'
    registry=ROOT/'data/curated/paper_taxonomy.csv'
    rebuilt=build_registry(papers,registry)
    output=tmp_path/'taxonomy.csv'
    write_registry(rebuilt,output)
    assert read_paper_taxonomy_registry(output)==read_paper_taxonomy_registry(registry)
    assert rebuilt==build_registry(papers,output)
    current=json.loads(papers.read_text())['records']
    maps=json.loads((ROOT/'web/data/public_preview_map_data.json').read_text())['records']
    summary=apply_paper_taxonomy_registry(current,maps,rebuilt,read_exclusion_rows())
    assert summary['public_papers_matched']==len(current)
    assert summary['map_records_matched']==len(maps)
    assert summary['registry_rows_suppressed_by_active_exclusion']==44


def test_generated_key_paper_reports_are_current_and_scoped():
    from scripts.audit_key_paper_coverage import validate_artifacts
    assert validate_artifacts()==[]
    result=batch_a_validation_receipt()
    assert result['key_paper_report_changes']=={'26':['map_record_count'],'218':['matched_public_title']}


def correction_fixture():
    old={'id':'example','doi':'10.1234/example','title':'Example image paper','year':2024,
         'institution':'Example Institute','institution_id':'institution:example',
         'latitude':10.0,'longitude':20.0,'institution_authors':['First Author','Second Author']}
    override={'title':old['title'],'year':2024,'institution':old['institution'],
              'authors':['First Author'],'notes':'Reviewed source: https://example.org/paper'}
    return old,override,{**old,'institution_authors':['First Author']}


def test_shrinkage_guard_accepts_exact_reviewed_author_correction():
    old,override,new=correction_fixture()
    result=analyze_shrinkage([old],[new],[old],[new],institution_author_overrides=[override])
    assert result.allowed
    assert result.removed_maps[0].explained
    assert 'curated institution-author correction' in result.removed_maps[0].evidence


@pytest.mark.parametrize('field,value',[('latitude',11.0),('longitude',21.0),
    ('institution_id','institution:other'),('doi','10.1234/another'),
    ('institution_authors',['Third Author'])])
def test_author_correction_cannot_authorize_unrelated_relation_change(field,value):
    old,override,new=correction_fixture();new[field]=value
    # A distinct DOI plus no shared title cannot be the same work.
    if field=='doi':new['title']='Different paper'
    result=analyze_shrinkage([old],[new],[old],[new],institution_author_overrides=[override])
    assert not result.allowed


@pytest.mark.parametrize('field,value',[('year',2023),('title','Different paper'),('institution','Other Institute')])
def test_unmatched_review_cannot_authorize_author_removal(field,value):
    old,override,new=correction_fixture();override[field]=value
    assert not analyze_shrinkage([old],[new],[old],[new],institution_author_overrides=[override]).allowed


def test_detail_rebuild_corrects_stale_nested_indices_and_is_idempotent():
    snapshot=snapshot_bytes()
    paper=next(r for r in json.loads(snapshot['web/data/public_preview_papers.json'])['records'] if r.get('arxiv_id')=='2007.10466')
    maps=[r for r in json.loads(snapshot['web/data/public_preview_map_data.json'])['records'] if r.get('arxiv_id')=='2007.10466']
    overrides=load_institution_author_overrides(ROOT/'data/curated/institution_author_overrides.csv')
    add_public_detail_fields([paper],maps,overrides)
    first=copy.deepcopy((paper,maps))
    add_public_detail_fields([paper],maps,overrides)
    assert (paper,maps)==first
    assert paper['author_institution_affiliations'][0]['authors']==overrides[0]['authors']
    assert all(a['name']!='Michael Goebel' or a['affiliation_indices']==[1] for a in paper['authors'])
