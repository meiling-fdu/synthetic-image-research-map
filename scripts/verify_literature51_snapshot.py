#!/usr/bin/env python3
"""Verify the completed literature batch using only a Git checkout's inputs.

Run in an isolated index/tree checkout:
  python3 scripts/verify_literature51_snapshot.py --require-isolated --regenerate
No retrieval, paper import, metadata migration or authoritative export writes.
Legacy ignored export inputs are restored from committed lossless archives.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import redirect_stdout
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

try:
    from . import integrate_literature51_2026_10_16 as batch
    from . import reassess_literature51_2026_10_16 as followup
    from .literature51_reproducibility import materialize_export_inputs, preserved_bytes, verify_workspace_files
except ImportError:
    import integrate_literature51_2026_10_16 as batch
    import reassess_literature51_2026_10_16 as followup
    from literature51_reproducibility import materialize_export_inputs, preserved_bytes, verify_workspace_files

ROOT = Path(__file__).resolve().parents[1]


def historical_failures(content):
    result={}
    for case in ET.fromstring(content).iter('testcase'):
        failure=case.find('failure')
        if failure is not None:
            name=case.get('classname').removeprefix('tests.')+'::'+case.get('name')
            result[name]=failure.get('message','')
    return result


def verify(root=ROOT, *, require_isolated=False):
    if (root/batch.OUT/'main_integration/manifest.json').exists():
        from scripts.verify_literature51_main_integration import check as check_main
        result = check_main(root)
        if require_isolated:
            assert result['workspace_verification_scope']=='isolated_checkout_local_files_absent'
        return result
    baseline=batch.read(root/batch.OUT/'baseline.json')
    scope=verify_workspace_files(root,baseline['untracked_sha256'])
    if require_isolated:
        assert scope=='isolated_checkout_local_files_absent'
    restored=materialize_export_inputs(root)
    untracked=set(subprocess.check_output(['git','ls-files','-o','--exclude-standard','-z'],cwd=root).decode().rstrip('\0').split('\0'))-{''}
    if require_isolated:
        assert untracked<=set(restored),'Unexpected untracked input in isolated checkout'
    integrity=batch.check(root)
    assert integrity['counts']=={'import':39,'held':12}
    plan=batch.read(root/batch.OUT/'plan.json')
    event=followup.receipt(root)
    review=batch.read(root/followup.OUT/'review.json')
    imported={a['candidate_id']:a['paper_id'] for a in plan['audit'] if a['decision']=='import'}
    imported.update({'B03':event['paper_id']})
    held=set(review['held'])
    assert len(imported)==39 and len(held)==12
    assert not set(imported)&held
    assert set(imported)|held==set(batch.EXPECTED)
    papers=batch.read(root/'web/data/public_preview_papers.json')['records']
    maps=batch.read(root/'web/data/public_preview_map_data.json')['records']
    assert len(papers)==678
    assert sum(p['publication_type'] in ('journal','conference','book') for p in papers)==561
    assert len(maps)==1421
    assert sum(bool(p['has_map_location']) for p in papers)==617
    assert sum(t['taxonomy_status']=='needs_review' for t in batch.rows(root/'data/curated/paper_taxonomy.csv'))==14
    ids={p.get('paper_id') for p in papers}
    assert set(imported.values())<=ids
    for a in plan['audit']:
        if a['candidate_id'] in held:
            assert not batch.identity_matches(a,{'public':papers}),a['candidate_id']
    for field,normalize in [('title',batch.title_key),('doi',batch.normalize_doi),('arxiv_id',batch.normalize_arxiv_id)]:
        values=Counter(normalize(p.get(field)) for p in papers if normalize(p.get(field)))
        assert not {k:n for k,n in values.items() if n>1},field
    assert len(ids-{None})==sum(bool(p.get('paper_id')) for p in papers),'Duplicate paper IDs'
    old_maps=json.loads(gzip.decompress((root/batch.OUT/'public_preview_map_data.json.before.gz').read_bytes()))
    assert maps==old_maps['records']
    by_title={batch.title_key(p['title']):p for p in papers}
    old_papers=json.loads(gzip.decompress((root/followup.OUT/'public_papers.before.gz').read_bytes()))['records']
    drift=[]
    for old in old_papers:
        new=by_title[batch.title_key(old['title'])]
        if old!=new:
            assert old.get('paper_id')=='curated:fa41c2810887fb216f5d'
            assert {k for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}=={'taxonomy_status','taxonomy_review'}
            assert new['taxonomy_status']=='reviewed'
            drift.append(old['paper_id'])
    assert len(drift)==1
    exclusion='data/curated/paper_exclusions.csv'
    assert batch.sha(root/exclusion)==baseline['tracked_sha256'][exclusion]
    prefix=batch.OUT/'test_results'
    initial=historical_failures(preserved_bytes(root,str(prefix/'baseline-full.xml')))
    final=historical_failures(preserved_bytes(root,str(prefix/'full-final.xml')))
    assert len(final)==4 and all(initial.get(k)==v for k,v in final.items())
    return {'candidate_count':51,'imported':39,'held':12,'unexplained':0,
        'public_papers':678,'formally_published':561,'map_relationships':1421,
        'taxonomy_pending':14,'duplicate_identities':0,'existing_public_objects_unchanged':676,
        'approved_taxonomy_review_change':drift,'map_objects_and_order_preserved':True,
        'historical_reviews_and_exclusions_preserved':True,'workspace_scope':scope,
        'restored_committed_inputs':restored,'declared_materialized_untracked':sorted(untracked&set(restored)),
        'unexpected_untracked_inputs':sorted(untracked-set(restored)),
        'historical_full_suite_failures':final}


def regenerate(root=ROOT):
    try:
        from . import export_public_preview as exporter
    except ImportError:
        import export_public_preview as exporter
    names=('public_preview_map_data.json','public_preview_papers.json')
    original={n:(root/'web/data'/n).read_bytes() for n in names}
    with tempfile.TemporaryDirectory(prefix='literature51-canonical-check-') as name:
        stage=Path(name)
        for n,b in original.items():
            (stage/n).write_bytes(b)
        location=stage/'institution_location_review.csv'
        shutil.copyfile(root/'data/curated/institution_location_review.csv',location)
        for run in (1,2):
            output=io.StringIO()
            with redirect_stdout(output):
                status=exporter.main(['--preserve-existing','--output',str(stage/names[0]),
                    '--paper-output',str(stage/names[1]),'--location-review',str(location)])
            assert status==0,output.getvalue()
            for n in names:
                actual=(stage/n).read_bytes()
                if actual!=original[n]:
                    before=json.loads(original[n]);after=json.loads(actual)
                    differences=[k for k in before.keys()|after.keys() if before.get(k)!=after.get(k)]
                    details={}
                    if 'records' in differences:
                        old={batch.title_key(p['title'])+'|'+str(p.get('institution_id',''))+'|'+str(p.get('location_id','')):p for p in before['records']}
                        for record in after['records']:
                            key=batch.title_key(record['title'])+'|'+str(record.get('institution_id',''))+'|'+str(record.get('location_id',''))
                            if key in old and old[key]!=record:
                                details[record['title']]=[k for k in old[key].keys()|record.keys() if old[key].get(k)!=record.get(k)]
                                if len(details)>=5:
                                    break
                    raise AssertionError(f'Canonical run {run} differs: {n}: {differences}; record fields: {details}')
    return {'canonical_runs':2,'byte_identical_to_staged_exports':True,
            'sha256':{n:hashlib.sha256(b).hexdigest() for n,b in original.items()}}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-isolated',action='store_true')
    parser.add_argument('--regenerate',action='store_true')
    args=parser.parse_args()
    result=verify(require_isolated=args.require_isolated)
    if args.regenerate:
        result['regeneration']=regenerate()
    print(json.dumps(result,ensure_ascii=False,indent=2))
