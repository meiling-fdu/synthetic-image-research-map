#!/usr/bin/env python3
"""Read-only row, field, identity, relationship and file guards for Batch A."""
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

try:
    from . import validate_corpus_quality_audit as audit
    from .corpus_quality_history import snapshot_bytes, predecessor_root
    from .remediate_corpus_quality_batch_a import APPROVED, OUT, ROOT, csv_bytes
    from .migrate_systematic_gap_2026_10_03 import csv_delta_bytes
    from .title_normalization import canonical_paper_title
except ImportError:
    import validate_corpus_quality_audit as audit
    from corpus_quality_history import snapshot_bytes, predecessor_root
    from remediate_corpus_quality_batch_a import APPROVED, OUT, ROOT, csv_bytes
    from migrate_systematic_gap_2026_10_03 import csv_delta_bytes
    from title_normalization import canonical_paper_title

CHANGED_FILES = {
    'data/curated/papers.csv', 'data/curated/paper_taxonomy.csv',
    'data/curated/author_institution_mappings.csv',
    'web/data/public_preview_papers.json', 'web/data/public_preview_map_data.json',
    'scripts/export_candidate_map_data.py', 'scripts/export_public_preview.py',
    'scripts/public_export_guard.py', 'scripts/validate_corpus_quality_audit.py',
    'tests/test_corpus_quality_audit.py', 'tests/test_systematic_gap_migration_2026_10_03.py',
    'tests/test_paper_taxonomy_migration.py',
    'data/curated/venue_aliases.csv', 'data/manual/key_paper_coverage_report.csv',
    'docs/key_paper_coverage_report.md',
    'scripts/gap_migration_history.py', 'tests/baseline_expectations.py',
    'tests/test_frontend_published_only_filter.py', 'tests/test_paper_metadata_consistency_audit.py',
}
NEW_FILES = {
    'data/curated/institution_author_overrides.csv', 'data/curated/publication_overrides.csv',
    'scripts/corpus_quality_history.py', 'scripts/remediate_corpus_quality_batch_a.py',
    'scripts/validate_corpus_quality_batch_a.py', 'tests/test_corpus_quality_batch_a.py',
    'docs/corpus_quality_batch_a_remediation_2026_10_04.md',
} | {'data/raw/corpus_quality_batch_a_2026_10_04/'+name for name in (
    'baseline.json','predecessor_640.json.gz','predecessor_640_manifest.json',
    'plan.json','results.json','validation.json','verification.json')}
PUBLICATION_FIELDS = {'title','year','publication_year','doi','publication_type',
    'venue','venue_name','venue_id','venue_type','venue_acronym','venue_track','venue_label',
    'venue_aliases','raw_venue','paper_url','formal_url','url','primary_url','is_arxiv_preprint',
    'metadata_source','metadata_status','curation_status'}
URL_FIELDS = {'paper_url','formal_url','primary_url','url','landing_page_url','notes','is_arxiv_preprint'}
AFFILIATION_FIELDS = {'authors','institution_authors','author_affiliation_indices',
    'author_institution_indices','author_institution_affiliations','affiliations',
    'current_institution','map_record_count','notes'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relationship_counts(maps, taxonomy):
    index = audit.PaperIdentityIndex(taxonomy, audit.PaperIdentityCache())
    pairs, links = Counter(), Counter()
    for r in maps:
        match=index.matches(r)
        if len(match)!=1:
            raise ValueError('Ambiguous relationship identity: '+r['id'])
        pid=match[0]['taxonomy_id']
        pairs[pid,r['institution_id']]+=1
        for author in r['institution_authors']:
            links[pid,r['institution_id'],author]+=1
    return {'rows':len(maps),'unique_pairs':len(pairs),
            'duplicate_pair_groups':sum(n>1 for n in pairs.values()),
            'repeated_author_institution_links':sum(n-1 for n in links.values()),
            'repeated_author_institution_groups':sum(n>1 for n in links.values())}


def validation_payload():
    errors=[]
    def check(ok, message):
        if not ok: errors.append(message)
    baseline=json.loads((OUT/'baseline.json').read_text())
    previous=snapshot_bytes()
    plan=json.loads((OUT/'plan.json').read_text())
    actions={r['review_id']:r for r in audit.decision_rows(audit.load_queues()) if r['batch']=='A'}
    check(set(actions)==APPROVED==set(plan['approved_review_ids']),'Batch A allowlist differs')
    grouped=defaultdict(list)
    for item in plan['updates']:grouped[item['file']].append(item)
    # Exact row/byte comparison ensures companion labels, other papers and manual
    # corrections cannot drift while the exporter is rebuilt.
    for path in previous:
        if path.startswith('data/curated/'):
            additions=plan.get('additions',{}).get(path,[])
            expected=csv_delta_bytes(previous[path],additions,grouped[path]) if grouped[path] or additions else previous[path]
            check((ROOT/path).read_bytes()==expected,'Unexpected curated content: '+path)
    for path,records in plan['new_csv'].items():
        check((ROOT/path).read_bytes()==csv_bytes(records),'Unexpected correction rows: '+path)
    with predecessor_root() as root:
        before=audit.load_context(root)
    after=audit.load_context()
    check(set(before['papers'])==set(after['papers']),'Paper identities added or removed')
    check(before['unmapped']==after['unmapped'],'Unmapped identities changed')
    check(audit.batch_counts(audit.load_queues())==dict(A=20,B=159,C=41,D=1752),'Original audit batches changed')
    permissions=defaultdict(set)
    for rid,action in actions.items():
        pid=action['paper_id']
        if rid[0] in 'TR':
            dim=action['dimension']
            permissions[pid]|={dim,'taxonomy_review'}
            check(after['papers'][pid][dim]==action['proposed_labels'],'Taxonomy action failed: '+rid)
            check(after['taxonomy'][pid][dim].split(';')==action['proposed_labels'],'Registry action failed: '+rid)
        elif rid in {'P018','P358','P572'}:
            permissions[pid]|=PUBLICATION_FIELDS
            actual=after['papers'][pid];old=before['papers'][pid]
            for field in ('year','publication_type','doi'):
                check(actual.get(field)==action['proposed_changes'][field],'Publication field failed: '+rid+' '+field)
            check(old['publication_type']=='preprint' and actual['publication_type']!='preprint','Formal transition failed: '+rid)
            check(actual['arxiv_id']==old['arxiv_id'] and actual.get('paper_id')==old.get('paper_id'),'Identity changed: '+rid)
            check([a['name'] for a in actual['authors']]==[a['name'] for a in old['authors']],'Author order changed: '+rid)
        elif rid=='P502':
            permissions[pid]|=URL_FIELDS
            actual=after['papers'][pid]
            check(actual['formal_url']==action['proposed_changes']['paper_url'],'LoRAX canonical URL missing')
            check(actual['venue_track']=='Workshop','LoRAX Workshop status changed')
        else:permissions[pid]|=AFFILIATION_FIELDS
    public_changes={};map_changes={}
    for pid in before['papers']:
        old,new=before['papers'][pid],after['papers'][pid]
        diff={f for f in old.keys()|new.keys() if old.get(f)!=new.get(f)}
        if diff:public_changes[pid]=sorted(diff)
        check(not diff-permissions[pid],'Unapproved public fields: '+pid+' '+str(sorted(diff-permissions[pid])))
    index=audit.PaperIdentityIndex(list(after['taxonomy'].values()),audit.PaperIdentityCache())
    taxonomy_pid={r['taxonomy_id']:pid for pid,r in after['taxonomy'].items()}
    old_maps=json.loads(previous['web/data/public_preview_map_data.json'])['records']
    new_maps=json.loads((ROOT/'web/data/public_preview_map_data.json').read_text())['records']
    old_by_id={r['id']:r for r in old_maps};new_by_id={r['id']:r for r in new_maps}
    check(not new_by_id.keys()-old_by_id.keys(),'Map identities added')
    removed=set(old_by_id)-set(new_by_id)
    r1=actions['L002'];r1pid=r1['paper_id']
    for ident in removed:
        old=old_by_id[ident]
        check(old.get('arxiv_id')=='2007.10466','Unrelated map identity removed: '+ident)
        # Prove the existing deterministic key collapses this corrected source
        # to a retained row without changing its institution or coordinates.
        corrected={**old,'institution_authors':r1['proposed_author_groups'][old['institution_id']]}
        try:
            from .public_relationships import public_relationship_key
        except ImportError:
            from public_relationships import public_relationship_key
        check(any(public_relationship_key(corrected)==public_relationship_key(r)
                  and all(old.get(f)==r.get(f) for f in ('latitude','longitude','institution_id','location_id'))
                  for r in new_maps),'Removed row is not an exact corrected duplicate: '+ident)
    for ident in old_by_id.keys()&new_by_id.keys():
        old,new=old_by_id[ident],new_by_id[ident]
        matches=index.matches(new)
        check(len(matches)==1,'Map identity mismatch: '+ident)
        pid=taxonomy_pid[matches[0]['taxonomy_id']]
        diff={f for f in old.keys()|new.keys() if old.get(f)!=new.get(f)}
        if diff:map_changes[ident]=sorted(diff)
        check(not diff-permissions[pid],'Unapproved map fields: '+ident+' '+str(sorted(diff-permissions[pid])))
    for path in ('web/data/public_preview_papers.json','web/data/public_preview_map_data.json'):
        old=json.loads(previous[path]);new=json.loads((ROOT/path).read_text())
        check({k:v for k,v in old.items() if k not in {'records','metadata'}}=={k:v for k,v in new.items() if k not in {'records','metadata'}},'Institution/hierarchy top-level data changed: '+path)
    for r in new_maps:
        if r.get('arxiv_id')=='2007.10466':
            check(r['institution_authors']==r1['proposed_author_groups'][r['institution_id']],'UCSB author correction failed: '+r['id'])
    affiliations={r['institution_id']:r['authors'] for r in after['papers'][r1pid]['author_institution_affiliations']}
    check(affiliations==r1['proposed_author_groups'],'UCSB paper-level author correction failed')
    check([r['name'] for r in after['papers'][r1pid]['authors']]==[r['name'] for r in before['papers'][r1pid]['authors']],'UCSB paper author order changed')
    report_path='data/manual/key_paper_coverage_report.csv'
    old_report={r['checklist_row']:r for r in csv.DictReader(io.StringIO(previous[report_path].decode()))}
    new_report={r['checklist_row']:r for r in csv.DictReader(io.StringIO((ROOT/report_path).read_text()))}
    check(set(old_report)==set(new_report),'Key-paper checklist identities changed')
    report_changes={key:sorted(f for f in old_report[key] if old_report[key][f]!=new_report[key][f])
                    for key in old_report.keys()&new_report.keys() if old_report[key]!=new_report[key]}
    check(report_changes=={'26':['map_record_count'],'218':['matched_public_title']},
          'Unexpected key-paper coverage changes: '+str(report_changes))
    check(new_report['26']['map_record_count']=='2','UCSB key-paper aggregate count stale')
    check(new_report['218']['matched_public_title']==canonical_paper_title(actions['P358']['proposed_changes']['title']),
          'LADLE-MM key-paper canonical title stale')
    original=json.loads((ROOT/audit.AUDIT/'baseline.json').read_text())
    changed=audit.changed_paths(ROOT,baseline['tracked_sha256'])
    changed_existing=audit.changed_paths(ROOT,baseline['untracked_sha256'])
    untracked=set(subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT).decode().strip('\0').split('\0'))
    unexpected=sorted((set(changed)|set(changed_existing))-CHANGED_FILES
                      | (untracked-set(baseline['untracked_sha256'])-NEW_FILES))
    frozen=audit.changed_paths(ROOT,original['frozen_neurips_sha256'])
    locals_changed=audit.changed_paths(ROOT,original['preexisting_local_sha256'])
    check(not unexpected,'Unexpected changed files: '+str(unexpected))
    check(not frozen,'Frozen NeurIPS changed')
    check(not locals_changed,'Preexisting local files changed')
    check(not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT),'Index is not empty')
    check(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==baseline['head'],'HEAD changed')
    def taxonomy_counts(context):
        return {d:dict(Counter(v for p in context['papers'].values() for v in p[d])) for d in ('tasks','research_types')}
    ledger=json.loads((OUT/'results.json').read_text())
    applied={r['review_id'] for r in ledger['records'] if r['status']=='APPLIED'}
    check(applied==APPROVED,'Remediation ledger does not reconcile to 20 applied actions')
    remaining=Counter(r['batch'] for r in audit.decision_rows(audit.load_queues()) if r['review_id'] not in applied)
    check(dict(remaining)==dict(B=159,C=41,D=1752),'Remaining decision counts changed')
    return {'before':before['counts'],'after':after['counts'],
            'taxonomy_before':taxonomy_counts(before),'taxonomy_after':taxonomy_counts(after),
            'relationships_before':relationship_counts(old_maps,list(before['taxonomy'].values())),
            'relationships_after':relationship_counts(new_maps,list(after['taxonomy'].values())),
            'changed_public_papers':public_changes,'changed_map_records':map_changes,'removed_map_ids':sorted(removed),
            'key_paper_report_changes':report_changes,
            'expected_changed':sorted((set(changed)|set(changed_existing))&CHANGED_FILES),
            'new_files':sorted(untracked-set(baseline['untracked_sha256'])),
            'unexpected_changed':unexpected,'frozen_changed':frozen,'preexisting_local_changed':locals_changed,
            'remaining_batches':dict(remaining),'R3':'REQUIRES_MAINTAINER_DECISION',
            'errors':errors}


def main():
    result=validation_payload()
    for key,field in [('UNEXPECTED_CHANGED','unexpected_changed'),('FROZEN_NEURIPS_CHANGED','frozen_changed'),('PREEXISTING_LOCAL_FILES_CHANGED','preexisting_local_changed')]:
        print(key+' = '+str(len(result[field])))
    print(json.dumps({k:v for k,v in result.items() if k not in {'changed_public_papers','changed_map_records'}},indent=2))
    return int(bool(result['errors']))


if __name__=='__main__':
    raise SystemExit(main())
