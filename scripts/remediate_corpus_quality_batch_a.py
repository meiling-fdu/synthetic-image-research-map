#!/usr/bin/env python3
"""Apply only the 20 approved 2026-10-04 corpus-quality actions; never publish."""
import argparse
import collections
import csv
import io
import json
from pathlib import Path

try:
    from . import validate_corpus_quality_audit as audit
    from .corpus_quality_history import snapshot_bytes
    from .migrate_systematic_gap_2026_10_03 import csv_delta_bytes
    from .venues import read_venue_aliases
    from .title_normalization import canonical_paper_title
except ImportError:
    import validate_corpus_quality_audit as audit
    from corpus_quality_history import snapshot_bytes
    from migrate_systematic_gap_2026_10_03 import csv_delta_bytes
    from venues import read_venue_aliases
    from title_normalization import canonical_paper_title

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/raw/corpus_quality_batch_a_2026_10_04'
DATE = '2026-10-04'
APPROVED = {'T403','T495','T610','R063','R074','R131','R210','R326','R346',
            'R388','R496','R528','R573','R614','P018','P358','P572','P502','L002','L029'}


def save(name, value):
    (OUT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def rows(value):
    return list(csv.DictReader(io.StringIO(value.decode(), newline='')))


def csv_bytes(records):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(records)
    return stream.getvalue().encode()


def prepare():
    snapshot = snapshot_bytes()
    queues = audit.load_queues()
    actions = {r['review_id']: r for r in audit.decision_rows(queues) if r['batch']=='A'}
    assert set(actions) == APPROVED
    originals = {p: rows(value) for p, value in snapshot.items() if p.endswith('.csv')}
    changed = {}
    results = []
    def update(path, key, identity, fields):
        before = next(r for r in originals[path] if r[key]==identity)
        item = changed.setdefault((path,identity), {'file':path,'key':key,'identity':identity,
                                                  'before':before,'after':dict(before)})
        item['after'].update(fields)
    taxonomy_path = 'data/curated/paper_taxonomy.csv'
    paper_path = 'data/curated/papers.csv'
    for rid, action in sorted(actions.items()):
        pid = action['paper_id']
        result = {'review_id':rid,'paper_id':pid,'title':action['title'],'date':DATE,
                  'authoritative_evidence':action.get('evidence_urls') or [action['evidence_url']],
                  'original_finding':str(audit.AUDIT), 'status':'PENDING_VALIDATION'}
        if rid[0] in 'TR':
            dim = action['dimension']
            matches = [r for r in originals[taxonomy_path] if r['paper_id']==pid or r['taxonomy_id']==pid]
            assert len(matches)==1
            tax = matches[0]
            assert tax[dim].split(';')==action['current_labels']
            fields = {dim:';'.join(action['proposed_labels']),dim+'_status':'reviewed',
                      dim+'_review_reason':f'Approved Batch A {rid}: '+action['reason'],
                      dim+'_evidence_source':action['evidence_url'],
                      dim+'_evidence_excerpt':action['reason'], 'audited_at':DATE}
            # Existing evidence tier is preserved; no newly retrieved evidence is claimed.
            update(taxonomy_path,'taxonomy_id',tax['taxonomy_id'],fields)
            if tax['paper_id'] and any(r['paper_id']==tax['paper_id'] for r in originals[paper_path]):
                update(paper_path,'paper_id',tax['paper_id'],{dim:fields[dim]})
            result.update(previous_value=action['current_labels'], applied_value=action['proposed_labels'], dimension=dim)
        elif rid in {'P018','P358','P572'}:
            proposed = dict(action['proposed_changes'])
            if 'title' in proposed:
                result['publisher_title_as_observed']=proposed['title']
                proposed['title']=canonical_paper_title(proposed['title'])
            assert action['current']['publication_type']=='preprint'
            venue_id = {'P018':'venue:acl','P358':'venue:computer-vision-and-image-understanding',
                        'P572':'venue:british-machine-vision-conference'}[rid]
            name = 'Annual Meeting of the Association for Computational Linguistics' if rid=='P018' else proposed['venue']
            fields = {**proposed,'year':str(proposed['year']),'venue':name,'venue_name':name,
                      'venue_id':venue_id,'venue_type':proposed['publication_type'],
                      'venue_track':proposed['venue_track'].lower(),'raw_venue':proposed['venue'],
                      'updated_at':DATE+'T00:00:00Z'}
            old = next(r for r in originals[paper_path] if r['paper_id']==pid)
            fields['metadata_source'] = 'primary-source review '+rid+'; '+action['reason']+'; '+proposed['paper_url']+'; prior metadata: '+old['metadata_source']
            update(paper_path,'paper_id',pid,fields)
            # Synchronize identity metadata only, preserving taxonomy labels and affiliations.
            identity = {k:fields.get(k,old[k]) for k in ('title','year','doi')}
            for path,key in [(taxonomy_path,'taxonomy_id'),('data/curated/author_institution_mappings.csv','mapping_id')]:
                for record in originals[path]:
                    if record['paper_id']==pid:
                        update(path,key,record[key],identity)
            result.update(previous_value=action['current'],applied_value=proposed)
        elif rid=='P502':
            result.update(previous_value={'paper_url':action['current']['paper_url']},applied_value=action['proposed_changes'])
        elif rid=='L002':
            maps=json.loads(snapshot['web/data/public_preview_map_data.json'])['records']
            previous=[r for r in maps if r.get('arxiv_id')=='2007.10466']
            result.update(previous_value=previous,applied_value=action['proposed_author_groups'])
        else:
            result.update(previous_value={'relationship_rows':1423,'unique_pairs':1422},
                          applied_value='Recompute with normal deterministic exporter; R3 remains REQUIRES_MAINTAINER_DECISION')
        results.append(result)
    lorax = actions['P502']; current=lorax['current']
    publication=[{'title':lorax['title'],'match_year':str(current['year']),
                  'formal_year':str(current['year']),'formal_venue':current['venue'],
                  'formal_doi':current['doi'],'formal_paper_url':lorax['proposed_changes']['paper_url'],
                  'publication_type':current['publication_type'],
                  'notes':'Approved Batch A P502; URL recovery only; Workshop preserved. Evidence: '+lorax['authoritative_source']}]
    r1=actions['L002']
    names={r['institution_id']:r['institution'] for r in json.loads(snapshot['web/data/public_preview_map_data.json'])['records'] if r.get('arxiv_id')=='2007.10466'}
    affiliations=[{'title':r1['title'],'year':'2021','institution':names[iid],
                   'authors':'; '.join(authors),
                   'notes':'Approved Batch A L002/R1; paper-time affiliations; '+r1['evidence_urls'][0]+' page 1. Original source rows preserved in remediation results; R3 requires maintainer decision.'}
                  for iid,authors in r1['proposed_author_groups'].items()]
    bmvc = next(r for r in read_venue_aliases() if r['alias']=='British Machine Vision Conference')
    bmvc['notes']='Approved Batch A P572: existing BMVC identity materialized from primary-source venue evidence; BMVC 2023 Main verified at https://papers.bmvc2023.org/0659.pdf. Track remains paper-level metadata.'
    plan={'approved_review_ids':sorted(APPROVED),'updates':list(changed.values()),
          'additions':{'data/curated/venue_aliases.csv':[bmvc]},
          'new_csv':{'data/curated/publication_overrides.csv':publication,
                     'data/curated/institution_author_overrides.csv':affiliations},'results':results}
    save('plan.json',plan)
    return plan


def apply():
    plan=json.loads((OUT/'plan.json').read_text())
    assert set(plan['approved_review_ids'])==APPROVED
    grouped=collections.defaultdict(list)
    for item in plan['updates']:
        grouped[item['file']].append(item)
    for path in plan.get('additions',{}):
        grouped.setdefault(path,[])
    snapshot=snapshot_bytes()
    for path,items in grouped.items():
        target=ROOT/path
        assert target.read_bytes()==snapshot[path], 'Input changed after baseline: '+path
        target.write_bytes(csv_delta_bytes(target.read_bytes(),plan.get('additions',{}).get(path,[]),items))
    for path,records in plan['new_csv'].items():
        assert not (ROOT/path).exists(), 'Refuse overwrite: '+path
        (ROOT/path).write_bytes(csv_bytes(records))
    save('results.json',{'date':DATE,'records':plan['results'],
                         'remaining_batches':{'B':159,'C':41,'D':1752},
                         'R3':'REQUIRES_MAINTAINER_DECISION'})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','apply'])
    args=parser.parse_args()
    {'prepare':prepare,'apply':apply}[args.command]()
