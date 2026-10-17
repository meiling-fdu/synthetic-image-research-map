#!/usr/bin/env python3
"""Reconcile and append the self-contained October 16 literature batch offline.

Raw captures and the candidate manifest are immutable inputs. reviewed.json is
the evidence adjudication layer, not a discovery feed. No manual files,
affiliations, coordinates, exclusions, validators, or historical locks are edited.
Run from any directory: python3 scripts/integrate_literature51_2026_10_16.py
Use --apply after inspecting plan.json; --check verifies the applied successor.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import tempfile
import unicodedata

try:
    from .curated_papers import normalize_paper_draft
    from .curated_schema import PAPERS_COLUMNS, PAPER_TAXONOMY_COLUMNS
    from .migrate_systematic_gap_2026_10_03 import csv_delta_bytes
    from .paper_exclusions import normalized_title_year_key
    from .paper_links import canonical_url, normalize_arxiv_id, normalize_doi
    from .review_decisions import upsert_review_decision
    from .venues import canonicalize_record, read_venue_aliases, create_canonical_venue, resolve_venue
except ImportError:
    from curated_papers import normalize_paper_draft
    from curated_schema import PAPERS_COLUMNS, PAPER_TAXONOMY_COLUMNS
    from migrate_systematic_gap_2026_10_03 import csv_delta_bytes
    from paper_exclusions import normalized_title_year_key
    from paper_links import canonical_url, normalize_arxiv_id, normalize_doi
    from review_decisions import upsert_review_decision
    from venues import canonicalize_record, read_venue_aliases, create_canonical_venue, resolve_venue

ROOT = Path(__file__).resolve().parents[1]
RAW = Path('data/raw/literature51_2026_10_16')
OUT = Path('data/processed/literature51_2026_10_16')
STAMP = '2026-10-16T10:00:00Z'
DIMENSIONS = ('tasks', 'image_scopes', 'research_types')
EXPECTED = [f'{group}{n:02}' for group, count in [('A',20),('B',3),('C',3),('D',6),('E',19)] for n in range(1,count+1)]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def title_key(value):
    value = html.unescape(re.sub('<[^>]*>', '', str(value or '')))
    return ''.join(c for c in unicodedata.normalize('NFKC', value).casefold() if c.isalnum())


def source_body(root, source):
    path = root / source['raw_path']
    body = gzip.decompress(path.read_bytes())
    if hashlib.sha256(body).hexdigest() != source['sha256']:
        raise ValueError(f'Raw source hash mismatch: {path}')
    # A few publisher responses themselves have Content-Encoding: gzip.
    while body.startswith(b'\x1f\x8b'):
        body = gzip.decompress(body)
    return body.decode('utf-8', errors='replace')


class MetadataParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta = defaultdict(list)

    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            attributes = dict(attrs)
            key = attributes.get('name', attributes.get('property', '')).lower()
            if key and attributes.get('content'):
                self.meta[key].append(attributes['content'])


def extract_metadata(root=ROOT):
    try:
        from .collect_literature51_sources import cache_sources, optional_retrieval_bodies
    except ImportError:
        from collect_literature51_sources import cache_sources, optional_retrieval_bodies
    sources = cache_sources(root)
    optional = optional_retrieval_bodies(root)
    result = {}
    for source in sources:
        if source.get('status') != 200:
            continue
        if source.get('raw_path') in optional:
            continue  # Challenge/redirect responses have no usable paper metadata.
        text = source_body(root, source)
        if 'Verifying your browser' in text:
            continue  # HTTP 200 challenge pages are never bibliographic evidence.
        item = result.setdefault(source['candidate_id'], {'source_refs': []})
        item['source_refs'].append(source['raw_path'])
        if source['kind'] == 'crossref' or source['url'].startswith('https://api.crossref.org/works?'):
            data = json.loads(text)['message']
            if 'items' in data:
                expected = next(c for c in read(root/RAW/'candidates.json')['candidates'] if c['candidate_id'] == source['candidate_id'])
                data = next(d for d in data['items'] if title_key(d['title'][0]) == title_key(expected['title']))
            item['crossref'] = data
            item['crossref_source'] = source['url']
        elif '<meta' in text:
            parser = MetadataParser()
            parser.feed(text)
            if parser.meta.get('citation_title'):
                item['citation'] = dict(parser.meta)
                item['citation_source'] = source['url']
                match = re.search(r'<(?:div|blockquote)[^>]*(?:id="abstract"|class="abstract[^\"]*")[^>]*>(.*?)</(?:div|blockquote)>', text, re.S)
                if match:
                    item['abstract'] = ' '.join(html.unescape(re.sub('<[^>]*>', ' ', match[1])).split())
    return result, sorted(sources, key=lambda s:(s['candidate_id'],s['url']))


def identity_matches(candidate, datasets):
    titles = {title_key(candidate['title']), *(title_key(t) for t in candidate.get('title_aliases', []))}
    dois = {normalize_doi(candidate.get('doi'))} - {''}
    aids = {normalize_arxiv_id(candidate.get('arxiv_id'))} - {''}
    urls = {canonical_url(u) for u in candidate.get('source_urls', [])} - {''}
    matches = []
    for dataset, records in datasets.items():
        for r in records:
            reasons = []
            if title_key(r.get('title')) in titles:
                reasons.append('normalized_title')
            if normalize_doi(r.get('doi')) in dois:
                reasons.append('doi')
            if normalize_arxiv_id(r.get('arxiv_id'),r.get('arxiv_url')) in aids:
                reasons.append('arxiv_id')
            if any(canonical_url(r.get(f)) in urls for f in ('paper_url','primary_url','url','formal_url','official_url')):
                reasons.append('canonical_url')
            if reasons:
                matches.append({'dataset':dataset,'paper_id':r.get('paper_id',''),
                                'decision_id':r.get('decision_id',''),'title':r.get('title',''),
                                'action':r.get('action',''),'matched_by':reasons})
    return matches


def identity_datasets(root):
    data = {name:rows(root/'data/curated'/name) for name in
            ['papers.csv','paper_taxonomy.csv','paper_exclusions.csv','review_decisions.csv',
             'paper_version_merges.csv','paper_arxiv_links.csv']}
    data['public_papers'] = read(root/'web/data/public_preview_papers.json')['records']
    data['public_map'] = read(root/'web/data/public_preview_map_data.json')['records']
    # These manifests are read for identity reconciliation; none is changed.
    data['historical_gap_decisions'] = read(root/'data/raw/systematic_gap_migration_2026_10_03/maintainer_decisions.json')
    locked = read(root/'data/manual/neurips_2026_targeted_gap_fill_reconciliation.json')
    data['neurips_locked'] = locked['records']
    return data


def prepare(root=ROOT):
    candidates = read(root/RAW/'candidates.json')['candidates']
    reviewed = read(root/OUT/'reviewed.json')
    assert [c['candidate_id'] for c in candidates] == EXPECTED
    assert set(reviewed) == set(EXPECTED)
    assert len({title_key(c['title']) for c in candidates}) == 51
    metadata, sources = extract_metadata(root)
    datasets = identity_datasets(root)
    additions = {'papers.csv':[], 'paper_taxonomy.csv':[], 'review_decisions.csv':[]}
    audit = []
    with tempfile.TemporaryDirectory(prefix='literature51-') as temp:
        venue_path = Path(temp)/'venue_aliases.csv'
        venue_path.write_bytes((root/'data/curated/venue_aliases.csv').read_bytes())
        decision_path = Path(temp)/'review_decisions.csv'
        decision_path.write_bytes((root/'data/curated/review_decisions.csv').read_bytes())
        for c in candidates:
            cid = c['candidate_id']; review = reviewed[cid]
            ident = {**c, **{k:review[k] for k in ('doi','arxiv_id','title_aliases') if k in review}}
            matches = identity_matches(ident, datasets)
            historic = [m for m in matches if m['dataset'] == 'review_decisions.csv']
            active = [m for m in matches if m['dataset'] in ('papers.csv','public_papers','public_map','paper_exclusions.csv')]
            item = {**c, **review, 'submitted_title':c['title'], 'identity_matches':matches, 'historical_reviews':historic, 'manual_review':review['decision'] == 'held', 'paper_id':''}
            if review['decision'] == 'import':
                if active:
                    raise ValueError(f'{cid}: existing identity requires reconciliation, not an append: {active}')
                locked = [m for m in matches if m['dataset'] == 'neurips_locked']
                if locked:
                    raise ValueError(f'{cid}: locked NeurIPS identity cannot be imported')
                if historic and not review.get('resolves_decision_ids'):
                    raise ValueError(f'{cid}: historical review needs an explicit linked resolution')
                if set(review.get('resolves_decision_ids',[])) != {m['decision_id'] for m in historic}:
                    raise ValueError(f'{cid}: historical review links differ')
                if not review.get('authors') or not review.get('evidence_sources'):
                    raise ValueError(f'{cid}: authors and primary evidence are mandatory')
                if not review['publication_verified']:
                    raise ValueError(f'{cid}: publication state is unresolved')
                evidence = metadata.get(cid,{})
                source_title = (evidence.get('crossref',{}).get('title') or evidence.get('citation',{}).get('citation_title') or [review['title']])[0]
                if title_key(source_title) not in {title_key(c['title']),title_key(review['title'])}:
                    raise ValueError(f'{cid}: supplied identifier resolves to a different title')
                if evidence.get('crossref') and normalize_doi(evidence['crossref']['DOI']) != normalize_doi(review.get('doi')):
                    raise ValueError(f'{cid}: DOI differs from its registration metadata')
                if review['evidence_tier'] == 'title' and not review.get('taxonomy_needs_review'):
                    raise ValueError(f'{cid}: title-only classifications must remain reviewable')
                aliases = read_venue_aliases(venue_path)
                venue = resolve_venue(review['venue'],publication_type=review['publication_type'],aliases=aliases)
                if venue.ambiguity_status != 'resolved':
                    create_canonical_venue({'venue_name':review['venue'], 'venue_acronym':review.get('venue_acronym',''),
                        'venue_type':review['publication_type'],'venue_track':review['venue_track'],
                        'raw_alias':review['venue'],'review_note':'Literature51 primary-source bibliographic verification: '+review['evidence_sources'][0],
                        'confirmed_similar':True},path=venue_path)
                    aliases = read_venue_aliases(venue_path)
                draft = normalize_paper_draft({**review, 'paper_url':review['primary_url'],
                    'source_database':'arxiv' if review['publication_type']=='preprint' else 'manual',
                    'scope_status':'in_scope','review_status':'reviewed'})
                draft = canonicalize_record({**draft,'venue_track':review['venue_track']}, aliases=aliases)
                if draft['venue_type']=='conference' and draft['venue_track']!=review['venue_track']:
                    raise ValueError(f'{cid}: conference track was defaulted')
                pid = 'curated:'+hashlib.sha256(normalized_title_year_key(draft).encode()).hexdigest()[:20]
                provenance = {'batch':str(OUT),'candidate_id':cid,'sources':review['evidence_sources'],
                    'publication_status':review['publication_status'],'publication_details':review.get('publication_details',{}),
                    'notes':review['notes'],'affiliations':'Unresolved; no institution identity or author-name inference.'}
                paper = {k:str(draft.get(k,'')) for k in PAPERS_COLUMNS}
                paper.update(paper_id=pid,metadata_source='Primary-source literature51 review: '+json.dumps(provenance,ensure_ascii=False),created_at=STAMP,updated_at=STAMP)
                additions['papers.csv'].append(paper)
                tax = {k:paper.get(k,'') for k in PAPER_TAXONOMY_COLUMNS}
                tax.update(taxonomy_id='paper_id:'+pid,taxonomy_status='needs_review' if review.get('taxonomy_needs_review') else 'reviewed',audited_at=STAMP)
                for dim in DIMENSIONS:
                    pending = dim in review.get('taxonomy_needs_review',[])
                    tax.update({dim+'_status':'needs_review' if pending else 'reviewed',
                        dim+'_review_reason':review['taxonomy_review_reason'] if pending else 'Literature51 evidence review 2026-10-16',
                        dim+'_evidence_tier':review['evidence_tier'],dim+'_evidence_source':'; '.join(review['evidence_sources']),
                        dim+'_evidence_excerpt':review['scope_rationale']})
                additions['paper_taxonomy.csv'].append(tax)
                item.update(paper_id=pid,canonical_title=paper['title'],manual_review=bool(review.get('taxonomy_needs_review')))
            note = (f'Literature51 {cid}: '+review['decision'].upper()+'. '+review['notes']+
                    ' Evidence: '+'; '.join(review['evidence_sources']))
            if review.get('resolves_decision_ids'):
                note += ' Supersedes disposition only; immutable historical rows retained: '+', '.join(review['resolves_decision_ids'])
            decision = upsert_review_decision({'review_queue':'manual_import','target_type':'paper',
                'title':review.get('title',c['title']),'year':review.get('year','2026'),'doi':ident.get('doi',''),
                'action':'add_paper' if review['decision']=='import' else 'unresolved',
                'review_note':note,'created_by':'literature51-2026-10-16'},path=decision_path)
            # The existing service owns validation/identity; batch time is fixed.
            decision.update(created_at=STAMP,updated_at=STAMP)
            additions['review_decisions.csv'].append(decision)
            item['new_review_decision_id'] = decision['decision_id']
            audit.append(item)
        old_venues = rows(root/'data/curated/venue_aliases.csv')
        additions['venue_aliases.csv'] = rows(venue_path)[len(old_venues):]
    plan = {'batch_id':'literature51_2026_10_16','prepared_at':STAMP,'candidate_count':51,
            'counts':dict(Counter(r['decision'] for r in audit)), 'audit':audit,'additions':additions,
            'input_sha256':{str(p.relative_to(root)):sha(p) for p in (root/'data/curated').glob('*.csv')},
            'reviewed_sha256':sha(root/OUT/'reviewed.json')}
    save(root/OUT/'extracted_metadata.json',metadata)
    save(root/RAW/'source_manifest.json',sources)
    save(root/OUT/'plan.json',plan)
    return plan


def apply(root=ROOT):
    receipt_path=root/OUT/'receipt.json'
    if receipt_path.exists():
        check(root)
        return read(receipt_path)  # Reruns cannot append duplicates.
    plan=read(root/OUT/'plan.json')
    for relative, expected in plan['input_sha256'].items():
        if sha(root/relative)!=expected:
            raise ValueError('Curated input changed since preparation: '+relative)
    if sha(root/OUT/'reviewed.json') != plan['reviewed_sha256']:
        raise ValueError('Reviewed evidence changed since preparation')
    # Recheck public/exclusion/review/alias identities at the mutation boundary.
    live=identity_datasets(root)
    for item in plan['audit']:
        if identity_matches(item,live) != item['identity_matches']:
            raise ValueError('Identity layer changed since preparation: '+item['candidate_id'])
    changes={}
    for name, additions in plan['additions'].items():
        path=root/'data/curated'/name
        changes[path]=csv_delta_bytes(path.read_bytes(),additions,[])
    # All schemas and identities are checked before any authoritative write.
    for path, content in changes.items():
        temporary=path.with_suffix('.csv.literature51.tmp')
        temporary.write_bytes(content)
        temporary.replace(path)
    receipt={'candidate_count':51,'counts':plan['counts'],
             'paper_ids':[p['paper_id'] for p in plan['additions']['papers.csv']],
             'curated_sha256':{str(p.relative_to(root)):sha(p) for p in changes}}
    save(receipt_path,receipt)
    check(root)
    return receipt


def check(root=ROOT):
    # Preserve both published-main changes and the immutable original receipts.
    if (root/OUT/'main_integration/manifest.json').exists():
        from scripts.verify_literature51_main_integration import check as check_main
        return check_main(root)
    try:
        from . import reassess_literature51_2026_10_16 as followup
        from .collect_literature51_sources import optional_retrieval_bodies
    except ImportError:
        import reassess_literature51_2026_10_16 as followup
        from collect_literature51_sources import optional_retrieval_bodies
    successor = followup.receipt(root)
    plan=read(root/OUT/'plan.json')
    assert sha(root/OUT/'reviewed.json')==plan['reviewed_sha256'],'Reviewed evidence changed after preparation'
    assert [r['candidate_id'] for r in plan['audit']]==EXPECTED
    assert sum(plan['counts'].values())==51
    assert len({title_key(r['title']) for r in plan['audit']})==51
    for name, additions in plan['additions'].items():
        path=root/'data/curated'/name
        # Compare original byte prefix, not just row counts or selected fields.
        before_path=root/OUT/(name+'.before.gz')
        if before_path.exists():
            before=gzip.decompress(before_path.read_bytes())
        else:
            import subprocess
            before=subprocess.check_output(['git','show',read(root/OUT/'baseline.json')['head']+':data/curated/'+name],cwd=root)
        original = csv_delta_bytes(before,additions,[])
        expected = followup.successor_bytes(name, original, successor) if successor else original
        assert path.read_bytes()==expected,name
    current=identity_datasets(root)
    for item in plan['audit']:
        matches=identity_matches(item,{'papers.csv':current['papers.csv']})
        imported = item['decision']=='import' or (successor and item['candidate_id'] in successor['released_candidates'])
        assert len(matches)==(1 if imported else 0),item['candidate_id']
    baseline=read(root/OUT/'baseline.json')
    allowed={'data/curated/'+name for name in plan['additions']} | {'web/data/public_preview_papers.json','web/data/public_preview_map_data.json'}
    boundary_path=root/OUT/'test_boundary_changes.json'
    if boundary_path.exists():
        for relative, evidence in read(boundary_path)['files'].items():
            assert evidence['before_sha256']==baseline['tracked_sha256'][relative]
            expected = successor.get('tracked_changes',{}).get(relative,{}).get('after_sha256',evidence['after_sha256']) if successor else evidence['after_sha256']
            assert sha(root/relative)==expected,relative
            allowed.add(relative)
    if successor:
        followup.check(root)
        allowed.update(successor.get('tracked_changes',{}))
    changed=[relative for relative,expected in baseline['tracked_sha256'].items()
             if relative not in allowed and sha(root/relative)!=expected]
    assert not changed,changed
    try:
        from .literature51_reproducibility import verify_workspace_files
    except ImportError:
        from literature51_reproducibility import verify_workspace_files
    workspace_scope = verify_workspace_files(root,baseline['untracked_sha256'])
    optional = optional_retrieval_bodies(root)
    for source in read(root/RAW/'source_manifest.json'):
        if source.get('raw_path'):
            if source['raw_path'] in optional and not (root/source['raw_path']).exists():
                continue
            source_body(root,source)
    return {'candidate_count':51,'counts':successor['counts'] if successor else plan['counts'],'historical_and_unrelated_files_preserved':True,
            'workspace_verification_scope':workspace_scope}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    command=parser.add_mutually_exclusive_group()
    command.add_argument('--apply',action='store_true')
    command.add_argument('--check',action='store_true')
    args=parser.parse_args()
    result=apply() if args.apply else check() if args.check else prepare()
    print(json.dumps({k:result[k] for k in ('candidate_count','counts')},indent=2))


if __name__=='__main__':
    main()
