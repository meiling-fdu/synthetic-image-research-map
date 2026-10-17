#!/usr/bin/env python3
"""Apply/check only the reviewed B03 release and E17 taxonomy follow-up offline.

The original 38/13 plan and receipts stay immutable. No discovery, batch replay,
institution changes or geocoding occurs. --apply is idempotent; --export uses
the canonical exporter, preserving 676 objects and E17's approved review change.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import tempfile
from contextlib import redirect_stdout

ROOT = Path(__file__).resolve().parents[1]
OUT = Path('data/processed/literature51_2026_10_16/followup')
STAMP = '2026-10-16T12:00:00Z'


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def digest(path):
    if path.exists():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    try:
        from .literature51_reproducibility import preserved_digest
    except ImportError:
        from literature51_reproducibility import preserved_digest
    root = next(parent for parent in path.parents if (parent/'data/processed/literature51_2026_10_16/baseline.json').exists())
    return preserved_digest(root,str(path.relative_to(root)))


def receipt(root=ROOT):
    path = root/OUT/'receipt.json'
    return read(path) if path.exists() else None


def local_only_paths(root=ROOT):
    """The reviewed file inventory identifies expendable local intermediates."""
    path = root/OUT/'file_audit.csv'
    if not path.exists():
        return set()
    event = receipt(root)
    if event and event.get('file_audit_sha256'):
        assert digest(path)==event['file_audit_sha256']
    with path.open(newline='') as stream:
        return {r['path'] for r in csv.DictReader(stream) if r['proposed_stage']=='false'}


def successor_bytes(name, original, review):
    try:
        from .migrate_systematic_gap_2026_10_03 import csv_delta_bytes
    except ImportError:
        from migrate_systematic_gap_2026_10_03 import csv_delta_bytes
    patches = review.get('patches',{}).get(name,[])
    if patches:
        stream = io.StringIO(original.decode('utf-8-sig'), newline='')
        reader = csv.DictReader(stream)
        rows = list(reader)
        for patch in patches:
            matches = [r for r in rows if r['paper_id']==patch['paper_id']]
            assert len(matches)==1
            row = matches[0]
            for key, value in patch['before'].items():
                assert row[key]==value, (name,key)
            row.update(patch['after'])
        output = io.StringIO(newline='')
        writer = csv.DictWriter(output, fieldnames=reader.fieldnames, lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
        original = output.getvalue().encode()
    return csv_delta_bytes(original,review.get('additions',{}).get(name,[]),[])


def apply(root=ROOT):
    if receipt(root):
        return check(root)
    try:
        from . import integrate_literature51_2026_10_16 as batch
        from .curated_schema import PAPERS_COLUMNS, PAPER_TAXONOMY_COLUMNS, REVIEW_DECISION_COLUMNS
        from .curated_papers import normalize_paper_draft
        from .paper_exclusions import normalized_title_year_key
    except ImportError:
        import integrate_literature51_2026_10_16 as batch
        from curated_schema import PAPERS_COLUMNS, PAPER_TAXONOMY_COLUMNS, REVIEW_DECISION_COLUMNS
        from curated_papers import normalize_paper_draft
        from paper_exclusions import normalized_title_year_key
    review = read(root/OUT/'review.json')
    baseline = read(root/OUT/'baseline.json')['current_sha256']
    for path in ('data/curated/papers.csv','data/curated/paper_taxonomy.csv',
                 'data/curated/review_decisions.csv','data/curated/venue_aliases.csv'):
        assert digest(root/path)==baseline[path],path
    b03 = review['released']['B03']
    datasets = batch.identity_datasets(root)
    existing = batch.identity_matches(b03,datasets)
    assert not [m for m in existing if m['dataset'] in ('papers.csv','public_papers','paper_exclusions.csv','neurips_locked')]
    old = next(r for r in batch.read(root/batch.OUT/'plan.json')['audit'] if r['candidate_id']=='B03')
    assert old['decision']=='held'
    draft = normalize_paper_draft({**b03,'source_database':'arxiv','scope_status':'in_scope','review_status':'reviewed'})
    pid = 'curated:'+hashlib.sha256(normalized_title_year_key(draft).encode()).hexdigest()[:20]
    paper = {k:str(draft.get(k,'')) for k in PAPERS_COLUMNS}
    paper.update(paper_id=pid,created_at=STAMP,updated_at=STAMP,
        metadata_source='Primary-source review Literature51 follow-up: '+json.dumps({
            'candidate_id':'B03','evidence':str(OUT/'review.json'),
            'publication_status':'preprint','version':'arXiv:2511.20722v2',
            'first_posted':'2025-11-25','revised':'2026-07-30',
            'accepted_only':'WIFS 2026 paper 137; no formal proceedings claimed',
            'title_aliases':b03['title_aliases'],
            'affiliations':'Unresolved mapping; original manuscript groups retained in review.json'
        },ensure_ascii=False))
    tax = {k:paper.get(k,'') for k in PAPER_TAXONOMY_COLUMNS}
    tax.update(taxonomy_id='paper_id:'+pid,taxonomy_status='reviewed',audited_at=STAMP)
    for dim in batch.DIMENSIONS:
        tax.update({dim+'_status':'reviewed',dim+'_review_reason':'Primary manuscript v2 objective and inpainting localization experiments reviewed',
            dim+'_evidence_tier':'primary_full_text',dim+'_evidence_source':b03['manuscript_url'],
            dim+'_evidence_excerpt':b03['scope_rationale']})
    # A new event references the immutable HOLD; never upsert over its identity.
    decision = {k:'' for k in REVIEW_DECISION_COLUMNS}
    decision.update(decision_id='review:'+hashlib.sha256(('literature51-followup-B03|'+pid).encode()).hexdigest()[:20],
        review_queue='manual_import',target_type='paper',title=paper['title'],year=paper['year'],
        action='add_paper',created_at=STAMP,updated_at=STAMP,created_by='literature51-followup-2026-10-16',
        review_note='Literature51 B03 released as one arXiv preprint. Supersedes disposition only: '+old['new_review_decision_id']+
        '. v1/v2 titles are one identity; use v2 ordered byline verified with HAL v2. WIFS paper 137 is accepted only. Evidence: '+str(OUT/'review.json'))
    e17 = next(r for r in batch.rows(root/'data/curated/paper_taxonomy.csv') if r['paper_id']=='curated:fa41c2810887fb216f5d')
    after = {'taxonomy_status':'reviewed','audited_at':STAMP}
    for dim in batch.DIMENSIONS:
        after.update({dim+'_status':'reviewed',dim+'_review_reason':'Saved CVF primary abstract reviewed; labels unchanged',
            dim+'_evidence_tier':'primary_abstract',dim+'_evidence_excerpt':review['taxonomy']['E17']['rationale']})
    event = {'released_candidates':['B03'],'counts':{'import':39,'held':12},'paper_id':pid,
        'superseded_decision_ids':[old['new_review_decision_id']],
        'review_sha256':digest(root/OUT/'review.json'),
        'cache_policy_sha256':digest(root/OUT/'cache_policy.json'),
        'additions':{'papers.csv':[paper],'paper_taxonomy.csv':[tax],'review_decisions.csv':[decision]},
        'patches':{'paper_taxonomy.csv':[{'paper_id':e17['paper_id'],'before':{k:e17[k] for k in after},'after':after}]},
        'tracked_changes':{}}
    changes = {root/'data/curated'/name:successor_bytes(name,(root/'data/curated'/name).read_bytes(),event)
               for name in event['additions']}
    for path, content in changes.items():
        path.write_bytes(content)
    save(root/OUT/'receipt.json',event)
    return {'counts':event['counts'],'paper_id':pid}


def check(root=ROOT):
    # The published-main successor has a different, explicitly pinned baseline.
    if (root/OUT.parent/'main_integration/manifest.json').exists():
        from scripts.verify_literature51_main_integration import check as check_main
        return check_main(root)
    event = receipt(root)
    assert event
    assert digest(root/OUT/'review.json')==event['review_sha256']
    assert digest(root/OUT/'cache_policy.json')==event['cache_policy_sha256']
    if event.get('evidence_index_sha256'):
        assert digest(root/OUT/'evidence_index.json')==event['evidence_index_sha256']
    if event.get('retrieval_manifest_sha256'):
        manifest = root/'data/raw/literature51_2026_10_16/followup/retrieval_manifest.json'
        assert digest(manifest)==event['retrieval_manifest_sha256']
        for source in read(manifest):
            if source.get('raw_path'):
                body=(root/source['raw_path']).read_bytes()
                if source['raw_path'].endswith('.gz'):
                    body=gzip.decompress(body)
                assert hashlib.sha256(body).hexdigest()==source['sha256']
    old = read(root/OUT.parent/'plan.json')
    assert old['counts']=={'import':38,'held':13}
    try:
        from .migrate_systematic_gap_2026_10_03 import csv_delta_bytes
    except ImportError:
        from migrate_systematic_gap_2026_10_03 import csv_delta_bytes
    for name, additions in old['additions'].items():
        original = csv_delta_bytes(gzip.decompress((root/OUT.parent/(name+'.before.gz')).read_bytes()),additions,[])
        assert (root/'data/curated'/name).read_bytes()==successor_bytes(name,original,event),name
    for path, value in event['tracked_changes'].items():
        assert digest(root/path)==value['after_sha256'],path
    baseline = read(root/OUT/'baseline.json')['current_sha256']
    immutable = read(root/OUT.parent/'baseline.json')['untracked_sha256']
    assert len(immutable)==130
    try:
        from .literature51_reproducibility import verify_workspace_files
    except ImportError:
        from literature51_reproducibility import verify_workspace_files
    workspace_scope = verify_workspace_files(root,immutable)
    optional = local_only_paths(root)
    for path in baseline:
        if path.startswith(('data/processed/literature51_2026_10_16/','data/raw/literature51_2026_10_16/')):
            if path in optional and not (root/path).exists():
                continue
            assert digest(root/path)==baseline[path],path
    return {'candidate_count':51,'counts':event['counts'],'historical_and_unrelated_files_preserved':True,
            'workspace_verification_scope':workspace_scope}


def export(root=ROOT):
    try:
        from . import export_public_preview as exporter, audit_key_paper_coverage as coverage
        from .public_export_metadata import atomic_write_json_files
    except ImportError:
        import export_public_preview as exporter, audit_key_paper_coverage as coverage
        from public_export_metadata import atomic_write_json_files
    event = receipt(root)
    before = read(root/OUT/'baseline.json')['current_sha256']
    with tempfile.TemporaryDirectory(prefix='literature51-followup-export-') as tmp:
        stage = Path(tmp)
        names = ('public_preview_map_data.json','public_preview_papers.json')
        for name in names:
            (stage/name).write_bytes((root/'web/data'/name).read_bytes())
        location = stage/'institution_location_review.csv'
        location.write_bytes((root/'data/curated/institution_location_review.csv').read_bytes())
        output = io.StringIO()
        with redirect_stdout(output):
            status = exporter.main(['--preserve-existing','--output',str(stage/names[0]),
                '--paper-output',str(stage/names[1]),'--location-review',str(location)])
        assert not status,output.getvalue()
        maps,papers = (read(stage/n) for n in names)
        old_papers = json.loads(gzip.decompress((root/OUT/'public_papers.before.gz').read_bytes()))
        old_maps = json.loads(gzip.decompress((root/OUT.parent/'public_preview_map_data.json.before.gz').read_bytes()))
        assert maps['records']==old_maps['records']
        current = {exporter.identity_key(p):p for p in papers['records']}
        assert len(old_papers['records'])==677
        drift = []
        for p in old_papers['records']:
            actual = current[exporter.identity_key(p)]
            expected = dict(p)
            if p.get('paper_id')=='curated:fa41c2810887fb216f5d':
                expected['taxonomy_status']='reviewed'
                expected['taxonomy_review']={dim:{'status':'reviewed',
                    'reason':'Saved CVF primary abstract reviewed; labels unchanged'}
                    for dim in ('tasks','image_scopes','research_types')}
            assert actual==expected,p['title']
            if actual!=p:
                drift.append({'paper_id':p['paper_id'],'fields':['taxonomy_status','taxonomy_review']})
        added = [p for p in papers['records'] if p.get('paper_id')==event['paper_id']]
        assert len(papers['records'])==678 and len(added)==1
        assert added[0]['publication_type']=='preprint' and not added[0]['has_map_location']
        atomic_write_json_files({root/'web/data'/name:read(stage/name) for name in names})
    artifacts,summary,errors = coverage.expected_artifacts()
    assert not errors,errors
    assert (root/coverage.OUT_PATH).read_bytes()==artifacts[coverage.OUT_PATH].encode()
    (root/coverage.MARKDOWN_PATH).write_text(artifacts[coverage.MARKDOWN_PATH])
    # Exact approved successor hashes; the original boundary receipt is retained.
    for path in ('tests/baseline_expectations.py','docs/key_paper_coverage_report.md'):
        event['tracked_changes'][path]={'before_sha256':before[path],'after_sha256':digest(root/path)}
    event['export']={'existing_public_papers_unchanged':676,'approved_existing_object_changes':drift,
        'map_relationships_unchanged':1421,
        'public_papers':678,'formally_published':561,'taxonomy_pending':14,
        'sha256':{name:digest(root/'web/data'/name) for name in names},
        'map_metadata_only_change':True,'unrelated_location_queue_written':False}
    save(root/OUT/'receipt.json',event)
    return check(root)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--apply',action='store_true')
    group.add_argument('--export',action='store_true')
    group.add_argument('--check',action='store_true')
    args = parser.parse_args()
    print(json.dumps(apply() if args.apply else export() if args.export else check(),indent=2))
