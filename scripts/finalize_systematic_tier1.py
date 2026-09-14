#!/usr/bin/env python3
"""Append reviewed Tier 1 records once, retaining the pre-insertion evidence."""
import csv
import hashlib
import io
import json
import shutil
from difflib import SequenceMatcher
from prepare_systematic_tier1 import ROOT, OUT
from reconcile_systematic_tier1 import reconcile, regular_name
from reconcile_systematic_literature import compact_title, read_csv
from venues import canonicalize_record

STAMP = '2026-09-13T00:00:00Z'


def append(name, additions):
    path = ROOT / 'data/curated' / name
    fields = next(csv.reader(path.open()))
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
    writer.writerows(additions)
    with path.open('ab') as handle:
        handle.write(stream.getvalue().encode())


def main():
    receipt = OUT / 'insertion.json'
    if receipt.exists():
        raise SystemExit('Already applied; use report_systematic_tier1.py for verification.')
    # Preserve all frozen historical inputs before refreshing derived exports.
    historical = json.loads((ROOT / 'data/processed/systematic_literature_2026_09/baseline_sha256.json').read_text())
    for relative, expected in historical.items():
        source = ROOT / relative
        assert hashlib.sha256(source.read_bytes()).hexdigest() == expected, relative
        dest = OUT / 'baseline' / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            shutil.copyfile(source, dest)
    reconcile()  # Strong identifiers and exclusions against the immediate live corpus.
    proposals = json.loads((OUT / 'proposals.json').read_text())
    papers = proposals['papers']
    assert len(papers) == 16 and all(p['outcome'] == 'MISSING_ADD' for p in papers)
    public = json.loads((ROOT / 'web/data/public_preview_papers.json').read_text())['records']
    corpus = public + read_csv(ROOT / 'data/curated/papers.csv')
    supplemental = []
    for p in papers:
        author_names = {compact_title(a) for a in p['authors']}
        acronym = p['title'].split(':')[0] if ':' in p['title'] else ''
        possible = []
        for c in corpus:
            authors = c.get('authors', [])
            if isinstance(authors, str):
                authors = authors.split(';')
            overlap = author_names & {compact_title(a if isinstance(a, str) else a.get('name', '')) for a in authors}
            same_venue_year = str(c.get('year')) == str(p['year']) and c.get('venue') == p['venue']
            acronym_match = bool(acronym and len(acronym.split()) <= 3 and acronym.casefold() in c['title'].casefold())
            if (len(overlap) >= 2 and same_venue_year) or acronym_match:
                possible.append({'title': c['title'], 'authors_overlap': sorted(overlap), 'acronym_match': acronym_match})
        supplemental.append({'candidate_id': p['candidate_id'], 'author_venue_year_or_acronym_candidates': possible})
    (OUT / 'supplemental_identity_checks.json').write_text(json.dumps(supplemental, indent=2) + '\n')
    reviewed_distinct = {
        'audit:98e7bf0da8264d5f': {'Pay Less Attention to Deceptive Artifacts: Robust Detection of Compressed Deepfakes on Online Social Networks'},
        'audit:745a864cbd6a6efc': {'FUSED: Forensic-Semantic Mixture-of-Experts for AI Inpainting Detection and Localization', 'Organic or Diffused: Can We Distinguish Human Art from AI-Generated Images?'},
    }
    for check in supplemental:
        assert {r['title'] for r in check['author_venue_year_or_acronym_candidates']} <= reviewed_distinct.get(check['candidate_id'], set())
        check['resolution'] = 'Distinct: ForenX introduces ForgReason and explainable general synthesis detection, whereas Pay Less Attention addresses compressed face deepfakes. FUSE fuses spectral and semantic cues; FUSED is a separate inpainting mixture-of-experts method with different authors/arXiv 2608.28302. Diffused is a substring collision in a human-art study.' if check['author_venue_year_or_acronym_candidates'] else 'No candidates.'
    (OUT / 'supplemental_identity_checks.json').write_text(json.dumps(supplemental, indent=2) + '\n')
    registry = read_csv(ROOT / 'data/curated/institutions.csv')
    aliases = read_csv(ROOT / 'data/curated/institution_aliases.csv')
    names = [r['canonical_name'] for r in registry] + [r['alias_name'] for r in aliases]
    inst_checks = []
    for inst in proposals['new_institutions']:
        name = inst['canonical_name']
        assert compact_title(name) not in {compact_title(n) for n in names}
        inst_checks.append({'name': name, 'registry_alias_exact_matches': [], 'similar_names': [n for n in names if SequenceMatcher(None, compact_title(name), compact_title(n)).ratio() >= .72], 'decision': 'Distinct institution in the primary author block. Similar spellings are not identity evidence; no merge or parent relationship inferred.'})
    (OUT / 'institution_identity_checks.json').write_text(json.dumps(inst_checks, indent=2, ensure_ascii=False) + '\n')
    new_papers, taxonomy, mappings = [], [], []
    for p in papers:
        provenance = 'Primary-source review 2026-09-13: ' + p['paper_url'] + '; ' + p['primary_pdf_url']
        row = {**p, 'authors': '; '.join(p['authors']), 'source_database': 'manual', 'metadata_source': provenance,
               'scope_status': 'in_scope', 'created_at': STAMP, 'updated_at': STAMP}
        for dim in ('tasks', 'image_scopes', 'research_types'):
            row[dim] = ';'.join(p[dim])
        row = canonicalize_record(row)
        new_papers.append(row)
        tax = {**row, 'taxonomy_id': 'paper_id:' + p['paper_id'], 'taxonomy_status': 'reviewed', 'audited_at': STAMP}
        for dim in ('tasks', 'image_scopes', 'research_types'):
            tax.update({dim + '_status': 'reviewed', dim + '_review_reason': '', dim + '_evidence_tier': 'primary_full_text', dim + '_evidence_source': p['primary_pdf_url'], dim + '_evidence_excerpt': p['taxonomy_evidence'][dim]})
        taxonomy.append(tax)
        for aff in p['affiliations']:
            if not aff['institution_id']:
                continue  # Preserve uncertainty in the review ledger, not a guessed mapping.
            order = 1 + sum(m['paper_id'] == p['paper_id'] for m in mappings)
            mappings.append({**{k: p[k] for k in ('paper_id', 'title', 'year', 'doi', 'openalex_url')},
                'mapping_id': 'mapping:' + hashlib.sha256((p['paper_id'] + ':' + str(order)).encode()).hexdigest()[:20],
                'institution': aff['institution'], 'institution_id': aff['institution_id'],
                'institution_authors': '; '.join(aff['authors']), 'author_order': str(min(p['authors'].index(a) + 1 for a in aff['authors'])),
                'affiliation_order': str(order), 'raw_affiliation': aff['raw_affiliation'],
                'provenance_source': p['primary_pdf_url'], 'mapping_status': 'active', 'created_at': STAMP, 'updated_at': STAMP})
    institutions = [{**i, 'institution_status': 'active', 'public_display': 'self', 'created_at': STAMP, 'updated_at': STAMP, 'created_by': 'primary-source-curation'} for i in proposals['new_institutions']]
    fuse = next(i for i in institutions if i['canonical_name'] == 'Southeast University (Bangladesh)')
    locations = [dict(location_id='location:' + hashlib.sha256(fuse['institution_id'].encode()).hexdigest()[:20], institution_id=fuse['institution_id'], institution=fuse['canonical_name'], normalized_institution='southeast university bangladesh', city='Dhaka', country='Bangladesh', country_code='BD', coordinate_status='unknown', created_at=STAMP, updated_at=STAMP, created_by='primary-source-curation')]
    additions = {'papers.csv': new_papers, 'paper_taxonomy.csv': taxonomy, 'author_institution_mappings.csv': mappings, 'institutions.csv': institutions, 'institution_locations.csv': locations}
    (OUT / 'planned_additions.json').write_text(json.dumps(additions, indent=2, ensure_ascii=False) + '\n')
    for name, rows in additions.items():
        append(name, rows)
    receipt.write_text(json.dumps({'date': STAMP, 'added': {n: len(r) for n, r in additions.items()}, 'paper_ids': [p['paper_id'] for p in papers], 'aliases': 0, 'hierarchy': 0}, indent=2) + '\n')


if __name__ == '__main__':
    main()
