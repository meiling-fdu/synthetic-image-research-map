#!/usr/bin/env python3
"""Check pending author/address evidence against actual exported institutions."""
import json
from prepare_systematic_tier1 import ROOT, OUT
from reconcile_systematic_literature import read_csv
from paper_exclusions import records_share_any_identity


def main():
    proposals = json.loads((OUT / 'proposals.json').read_text())['papers']
    papers = json.loads((ROOT / 'web/data/public_preview_papers.json').read_text())['records']
    markers = json.loads((ROOT / 'web/data/public_preview_map_data.json').read_text())['records']
    by_id = {p['paper_id']: p for p in papers if p.get('paper_id')}
    pending = []
    markerless = []
    for p in proposals:
        public = by_id[p['paper_id']]
        if not public['has_map_location']:
            markerless.append(public['title'])
        verified = {a for f in p['affiliations'] if f['institution_id'] for a in f['authors']}
        unverified = set(p['authors']) - verified
        assert {a['name'] for a in public['authors'] if not a['affiliation_indices']} == unverified
        for author in sorted(unverified):
            pending.append({'paper_id': p['paper_id'], 'author': author, 'evidence_notes': p['unresolved']})
        for marker in markers:
            if not records_share_any_identity(p, marker):
                continue
            authors = marker.get('institution_authors', [])
            if isinstance(authors, str):
                authors = [a.strip() for a in authors.split(';')]
            assert not unverified.intersection(authors), (p['title'], authors)
    assert len(pending) == 13 and len(markerless) == 6
    institutions = read_csv(ROOT / 'data/curated/institutions.csv')
    bd = next(i for i in institutions if i['canonical_name'] == 'Southeast University (Bangladesh)')
    cn = next(i for i in institutions if i['canonical_name'] == 'Southeast University')
    assert bd['institution_id'] != cn['institution_id']
    fuse = next(p for p in proposals if p['title'].startswith('FUSE:'))
    assert cn['institution_id'] not in {f['institution_id'] for f in fuse['affiliations']}
    review, = [r for r in read_csv(ROOT / 'data/curated/institution_location_review.csv')
               if r['institution_id'] == bd['institution_id'] and r['related_paper_id'] == fuse['paper_id']]
    assert (review['suggested_city'], review['suggested_country'], review['review_status'], review['coordinate_status']) == ('Dhaka', 'Bangladesh', 'pending_review', 'missing')
    assert review['evidence_source'] and review['evidence_url'].startswith('https://seu.edu.bd/')
    assert 'Tejgaon' in (ROOT / 'data/raw/systematic_tier1_2026_09/1a04ec79a4a910e0e011.html').read_text()
    assert not any(l['institution_id'] == bd['institution_id'] for l in read_csv(ROOT / 'data/curated/institution_locations.csv'))
    ntire = next(p for p in proposals if p['title'].startswith('NTIRE'))
    ntire_pending = {r['author'] for r in pending if r['paper_id'] == ntire['paper_id']}
    assert set(ntire['authors'][24:29]) | {'Cong Luo', 'Mikhail Erofeev'} == ntire_pending
    result = {'markerless_new_papers': markerless, 'authors_without_verified_institutional_mappings': pending,
              'fuse_bangladesh_entity_distinct': True, 'fuse_official_tejgaon_address_retained': True,
              'fuse_pending_review_without_coordinates': True, 'ntire_unresolved_authors_have_no_institution_marker': True}
    (OUT / 'final_location_audit.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print('Location/affiliation audit passed: 6 markerless papers, 13 authors without verified institutional mappings.')


if __name__ == '__main__':
    main()
