#!/usr/bin/env python3
"""Prepare insertion proposals from explicit Tier 1 primary review, never insert."""
import csv
import hashlib
import json
import re
from difflib import SequenceMatcher
from prepare_systematic_tier1 import ROOT, OUT
from verify_systematic_literature_sources import Metadata
from parse_systematic_literature import text
from reconcile_systematic_literature import compact_title, read_csv
from audit_key_paper_coverage import PaperIndex, identity_values, norm_title
from paper_exclusions import active_exclusions, exclusions_with_curated_identities, matching_exclusion_rows

LEDGER = ROOT / 'data/manual/systematic_tier1_primary_review_2026_09.json'
NEW_TYPES = {
    'Bitdefender': 'company', 'University Politehnica of Bucharest': 'university',
    'University of Neuchâtel': 'university', 'Delft University of Technology': 'university',
    'University of Turin': 'university', 'Fujitsu Research of America': 'company',
    'Smart City Research Institute of China Electronics Technology Group Corporation': 'research_unit',
    'Jiangsu Police Institute': 'university', 'BRAC University': 'university', 'Enosis Solutions': 'company',
    'Southeast University (Bangladesh)': 'university', 'MSU Institute for Artificial Intelligence': 'research_unit',
    'Lomonosov Moscow State University': 'university', 'University of Würzburg': 'university',
    'Ant International': 'company', 'IntSig Information Co. Ltd': 'company', 'Prince Sultan University': 'university',
    'Sogang University': 'university', 'National School of Artificial Intelligence': 'university',
}
PENDING_IDENTITIES = {'IBM Research', 'Trend Micro Incorporated', 'BASF Incorporated', 'BMW Incorporated', 'Geely Automobile Research Institute'}


def regular_name(value):
    if value.count(',') == 1:
        last, first = value.split(',')
        return first.strip() + ' ' + last.strip()
    return value.strip()


def reconcile():
    if (OUT / 'insertion.json').exists():
        raise SystemExit('Tier 1 insertion is complete. Preserve the pre-insertion proposals; use report_systematic_tier1.py to verify the current corpus.')
    candidates = json.loads((OUT / 'candidates.json').read_text())
    ledger = json.loads(LEDGER.read_text())['papers']
    sources = json.loads((OUT / 'sources.json').read_text())
    pdfs = json.loads((OUT / 'pdf_index.json').read_text())
    public = json.loads((ROOT / 'web/data/public_preview_papers.json').read_text())['records']
    curated = read_csv(ROOT / 'data/curated/papers.csv')
    corpus = public + curated
    index = PaperIndex(corpus)
    exclusions = active_exclusions(exclusions_with_curated_identities(read_csv(ROOT / 'data/curated/paper_exclusions.csv'), curated))
    institutions = {r['canonical_name']: r for r in read_csv(ROOT / 'data/curated/institutions.csv')}
    locations = read_csv(ROOT / 'data/curated/institution_locations.csv')
    result, new_institutions = [], {}
    for candidate in candidates:
        key = candidate['candidate_id'].split(':')[1]
        decision = ledger[key]
        ss = [s for s in sources if s['candidate_id'] == candidate['candidate_id']]
        primary = []
        for s in ss:
            if s['status'] != 200 or s['kind'] not in {'primary_html', 'version_primary'} or s.get('raw_path', '').endswith('.pdf'):
                continue
            parser = Metadata()
            body = (ROOT / s['raw_path']).read_text()
            parser.feed(body)
            m = parser.values
            title = (m.get('citation_title') or [''])[0]
            if compact_title(title) != compact_title(candidate['canonical_title']):
                continue
            abstract = (m.get('citation_abstract') or [''])[0]
            if not abstract:
                match = re.search(r'<(?:div|blockquote)[^>]*(?:id="abstract"|class="abstract[^"]*")[^>]*>(.*?)</(?:div|blockquote)>', body, re.S)
                abstract = text(match[1]) if match else ''
            primary.append({'source': s, 'title': text(title), 'authors': [regular_name(a) for a in m.get('citation_author', [])], 'abstract': text(abstract), 'metadata': m})
        assert primary, candidate['canonical_title']
        primary.sort(key=lambda p: ('arxiv' in p['source'].get('final_url', p['source']['url']), not bool(p['authors'])))
        p = primary[0]
        authors = decision.get('authors') or next(q['authors'] for q in primary if q['authors'])
        if key == 'd7a0be175acdedc4':
            authors = ['Dmitry Vatolin' if a == 'Dmitriy Vatolin' else a for a in authors]
        row = dict(candidate_id=candidate['candidate_id'], paper_id='curated:' + hashlib.sha256(('systematic-tier1:' + key).encode()).hexdigest()[:20],
                   title=p['title'], authors=authors, year=decision['year'], venue=decision['venue'], publication_type=decision['publication_type'],
                   doi=decision.get('doi', next((v for v in candidate['doi'].split(' | ') if v and '10.48550/' not in v), '')),
                   arxiv_id=decision.get('arxiv_id', candidate['arxiv_id']), openalex_url='',
                   paper_url=p['source']['url'], abstract=next((q['abstract'] for q in primary if q['abstract']), ''),
                   tasks=decision['tasks'], image_scopes=decision['image_scopes'], research_types=decision['research_types'],
                   taxonomy_evidence=decision['taxonomy_evidence'], code_url=decision.get('code_url', ''),
                   identity_note=decision.get('identity_note', ''), discovery_channels=candidate['discovery_channels'])
        evidence = [dict(title=candidate['canonical_title'], doi=v) for v in candidate['doi'].split(' | ') if v]
        evidence += [dict(title=candidate['canonical_title'], openalex_url='https://openalex.org/' + v.upper()) for v in candidate['openalex_id'].split(' | ') if v]
        evidence += [dict(row)] + [dict(title=t, year=row['year']) for t in decision.get('alternate_titles', [])]
        oa = []
        for s in ss:
            if s['status'] != 200 or s['kind'] not in {'openalex_identity', 'crossref_identity'}:
                continue
            data = json.loads((ROOT / s['raw_path']).read_text())
            for record in data.get('results', data.get('message', {}).get('items', [])):
                title = record.get('title', '')
                title = title[0] if isinstance(title, list) and title else title
                if compact_title(title) != compact_title(row['title']):
                    continue
                item = {'title': title, 'doi': record.get('doi', record.get('DOI', '')) or '', 'openalex_url': record.get('id', '')}
                evidence.append(item)
                if item['openalex_url']:
                    oa.append(item)
        if oa:
            oa.sort(key=lambda o: (row['doi'] not in o['doi'] if row['doi'] else '10.48550/' not in o['doi']))
            row['openalex_url'] = oa[0]['openalex_url']
        elif candidate['openalex_id']:
            # These IDs retain the exact-title cached discovery provenance from the completed audit.
            row['openalex_url'] = 'https://openalex.org/' + candidate['openalex_id'].split(' | ')[0].upper()
        matches, excluded, conflicts = [], [], []
        for e in evidence:
            i, kind, conflict = index.match(e)
            if i is not None:
                matches.append({'kind': kind, 'paper_id': corpus[i].get('paper_id'), 'title': corpus[i]['title']})
            if conflict:
                conflicts.append(conflict)
            excluded += matching_exclusion_rows(e, exclusions)
            excluded += [x for x in exclusions if compact_title(x['title']) == compact_title(e['title'])]
        excluded = list({e['exclusion_id']: e for e in excluded}.values())
        fuzzy = []
        for c in corpus:
            score = SequenceMatcher(None, norm_title(row['title']), norm_title(c['title'])).ratio()
            if score >= .78:
                fuzzy.append({'title': c['title'], 'paper_id': c.get('paper_id', ''), 'similarity': round(score, 4)})
        row.update(identity_checks=evidence, identity_matches=matches, identity_conflicts=conflicts, exclusion_ids=[e['exclusion_id'] for e in excluded], fuzzy_suggestions=list({x['title']: x for x in fuzzy}.values()))
        row['outcome'] = 'EXISTING_EXCLUSION' if excluded else 'EXISTING_CURRENT' if matches else 'AMBIGUOUS_IDENTITY' if conflicts else 'MISSING_ADD'
        pp = [e for e in pdfs if e['candidate_id'] == candidate['candidate_id']]
        pp.sort(key=lambda e: 'arxiv' in e['url'])
        assert pp
        row.update(primary_pdf=pp[0]['raw_path'], primary_pdf_url=pp[0]['url'], primary_text=pp[0]['text_path'], affiliation_pages=decision.get('affiliation_pages', [1]))
        row['unresolved'] = list(decision.get('unresolved', []))
        row['affiliations'] = []
        for name, orders, raw in decision['affiliations']:
            if name in PENDING_IDENTITIES:
                row['unresolved'].append(f'Canonical institution/site identity pending for {name}; primary author positions {orders} retained without an inferred registry match.')
                row['affiliations'].append(dict(institution=name, institution_id='', authors=[authors[i-1] for i in orders], raw_affiliation=raw, status='needs_review'))
                continue
            institution = institutions.get(name)
            if not institution:
                assert name in NEW_TYPES, name
                institution = new_institutions.setdefault(name, {'institution_id': 'institution:' + hashlib.sha256(('tier1:' + name).encode()).hexdigest()[:16], 'canonical_name': name, 'institution_type': NEW_TYPES[name], 'primary_evidence': row['primary_pdf_url']})
            institution_id = institution['institution_id']
            confirmed = [x for x in locations if x['institution_id'] == institution_id and x.get('coordinate_status') == 'known' and x.get('lat') and x.get('lon')]
            if not confirmed:
                row['unresolved'].append(f'No confirmed institutional location reused for {name}; no city-center coordinate assigned.')
            row['affiliations'].append(dict(institution=name, institution_id=institution_id, authors=[authors[i-1] for i in orders], raw_affiliation=raw, status='active'))
        assigned = {a for f in row['affiliations'] for a in f['authors']}
        row['unassigned_authors'] = [a for a in authors if a not in assigned]
        row['bibliography_status'] = 'reviewed'
        row['taxonomy_status'] = 'reviewed'
        row['affiliation_status'] = 'needs_review' if row['unassigned_authors'] or any(not a['institution_id'] for a in row['affiliations']) else 'reviewed'
        row['curation_status'] = 'needs_review' if row['unresolved'] else 'confirmed'
        row['review_status'] = 'needs_check' if row['unresolved'] else 'reviewed'
        result.append(row)
    (OUT / 'proposals.json').write_text(json.dumps({'papers': result, 'new_institutions': list(new_institutions.values())}, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps([{'title': r['title'], 'outcome': r['outcome'], 'authors': len(r['authors']), 'fuzzy': r['fuzzy_suggestions'], 'unassigned': r['unassigned_authors']} for r in result], indent=2))


if __name__ == '__main__':
    reconcile()
