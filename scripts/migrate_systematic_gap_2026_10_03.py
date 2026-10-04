#!/usr/bin/env python3
"""Apply only the reviewed October gap migration; never search or edit manual data.

`prepare` builds a reviewable, schema-shaped plan. `apply` checks the live inputs
and seven identity layers again, then writes the approved deltas once. Public
JSON is always produced separately by export_public_preview.py.
"""
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import re

try:
    from . import audit_gap_2026_10_02 as audit
    from .curated_papers import normalize_paper_draft
    from .title_normalization import canonical_paper_title
    from .paper_exclusions import normalized_title_year_key
    from .venues import canonicalize_record, read_venue_aliases
except ImportError:
    import audit_gap_2026_10_02 as audit
    from curated_papers import normalize_paper_draft
    from title_normalization import canonical_paper_title
    from paper_exclusions import normalized_title_year_key
    from venues import canonicalize_record, read_venue_aliases

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/raw/systematic_gap_migration_2026_10_03'
AUDIT = ROOT / 'data/raw/systematic_gap_audit_2026_10_02'
STAMP = '2026-10-03T00:00:00Z'
CREATOR = 'maintainer-approved-gap-migration'
DIMENSIONS = ('tasks', 'image_scopes', 'research_types')


def read(path):
    return json.loads(path.read_text())


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()[:20]


def rows(name):
    with (ROOT / 'data/curated' / name).open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def source_bytes(entry):
    return gzip.decompress((ROOT / entry['raw_path']).read_bytes())


def shaped(name, row):
    with (ROOT / 'data/curated' / name).open(newline='') as f:
        fields = next(csv.reader(f))
    return {key: str(row.get(key, '')) for key in fields}


def publication_details(c):
    if c['venue'] == 'ICML':
        source = next(s for s in read(AUDIT / 'source_manifest.json')
                      if s['url'].rstrip('/') == 'https://proceedings.mlr.press/v306')
        text = source_bytes(source).decode()
        slug = c['official_url'].rsplit('/', 1)[-1]
        block = next(b for b in text.split('<div class="paper">') if slug in b)
        pages = re.search(r'306:([0-9]+-[0-9]+)', block)[1]
        return {'volume': '306', 'pages': pages, 'proceedings_identity': 'pmlr-v306-' + slug[:-5]}
    if c['title'].startswith('Beyond Visual Forensics'):
        return {'volume': 'LNCS 16896', 'pages': '', 'pages_status': 'pending in official BibTeX'}
    if c['doi'] == '10.11834/jig.250624':
        return {'pages': '1-26', 'publication_note': 'Publisher online-first article, 2026; volume/issue pending.'}
    return {}


def maintainer_decisions(candidates, approved_ids):
    decisions = []
    notes = {
        'gap-597b9e58e04b': ('EXCLUDE_OUT_OF_SCOPE', 'SICA/OpenMMSec deliberately unifies AIGC, deepfake, manipulation and document forgery. AIGC is one component of a broad framework; excluded under the current narrow corpus policy, not a judgment of research relevance.'),
        'gap-44d3346b0c68': ('EXCLUDE_OUT_OF_SCOPE', 'OmniVL-Guard targets interleaved text/image/video misinformation detection and grounding; no independently central synthetic-image forensic contribution established.'),
        'gap-95d61d3debba': ('EXCLUDE_OUT_OF_SCOPE', 'Forensic Prompting is a generic framework spanning manual manipulation, diffusion, face and text settings; generative imagery is insufficiently dominant under the narrow policy.'),
        'gap-f6ee3e8afe33': ('EXCLUDE_OUT_OF_SCOPE', 'Chimera centers on counter-forensic detector evasion and digitally signed camera-provenance circumvention, not ordinary passive detection.'),
        'gap-475047af959c': ('HOLD_SCOPE_EVIDENCE_INSUFFICIENT', 'DiCoME abstract establishes generic deepfake detection, but independent general synthetic-image evaluation is unverified. Temporary evidence hold, not permanent exclusion.'),
        'gap-d59604897b0c': ('AMBIGUOUS_IDENTITY', 'arXiv:2511.02791 and SSRN 6032054 share authors and overlap but the SSRN title and experiments expand the scope. Preserve both links; establish neither one nor two corpus identities yet.')
    }
    for c in candidates:
        cid = c['candidate_id']
        if cid in approved_ids:
            status, note = 'APPROVE_ADD', 'Maintainer approved this work and canonical taxonomy for the 17-paper migration.'
        elif cid in notes:
            status, note = notes[cid]
        elif any(c['title'].startswith(s) for s in ('BM-DDFN:', 'SCA-Det:', 'Spectral Forensics:', 'Proto-LeakNet:')):
            status, note = 'HOLD_EVIDENCE_INSUFFICIENT', 'Retain original ambiguous/evidence-insufficient state. No addition, no permanent scope exclusion, no renewed discovery.'
        else:
            continue
        decisions.append({'candidate_id': cid, 'original_status': c['status'], 'decision': status,
                          'title': c['title'], 'note': note, 'decided_at': STAMP,
                          'source_urls': [c['official_url']] + [v['url'] for v in c.get('alternate_versions', [])]})
    return decisions


def live_reconciliation(papers):
    audit.corpus.cache_clear()
    audit.identity_layers.cache_clear()
    checks = []
    for p in papers:
        result = audit.compare(p)
        hits = set(v for values in result['exact_public'].values() for v in values)
        # A title in the rejected DRCT suggestion is not a canonical RA-Det row.
        canonical_rows = [r for r in rows('papers.csv') if (
            r['paper_id'] == p['paper_id'] or audit.normalize(r['title']) == audit.normalize(p['title'])
            or (p.get('doi') and audit.doi(r['doi']) == audit.doi(p['doi']))
            or (p.get('arxiv_id') and audit.arxiv(r['arxiv_id']) == audit.arxiv(p['arxiv_id'])))]
        hits.update(r['paper_id'] for r in canonical_rows)
        if len(hits) > 1:
            raise ValueError('Conflicting canonical identities: ' + p['title'])
        existing = next(iter(hits), '')
        note = 'No exact canonical identity. Top-three fuzzy titles and author/year overlaps are distinct works; shared task wording/coauthors do not establish identity.'
        if p['candidate_id'] == 'gap-847aa30be0f5':
            note += ' DNA acronym matches unrelated Dual-Stage Native Attribution; distinct title, authors, task and identifier.'
        if p['candidate_id'] == 'gap-923484c8a9ee':
            note += ' Historical key_papers_enriched.csv title suggestion belongs to rejected DRCT enrichment, not an accepted RA-Det identity. Never reuse that suggestion identity.'
        checks.append({'candidate_id': p['candidate_id'], 'title': p['title'], 'checks': result,
                       'existing_paper_id': existing, 'outcome': 'UPDATE_EXISTING' if existing else 'ADD_NEW',
                       'adjudication': note})
    return checks


def prepare():
    if (OUT / 'insertion.json').exists():
        raise ValueError('Migration already applied; inspect insertion.json and validation.json.')
    approved = read(OUT / 'approved_candidates.json')
    evidence = read(OUT / 'affiliation_review.json')
    all_candidates = read(AUDIT / 'candidates.json')['works']
    primary = {audit.normalize(c['title']): c for c in read(AUDIT / 'primary_metadata.json')}
    jobs = {r['candidate_id']: r['pdf_url'] for r in read(OUT / 'fetch_jobs.json')}
    manifest = read(OUT / 'source_manifest.json')
    jobs['gap-844d4535b37b'] = next(r['url'] for r in manifest if r['label'] == 'CJIG affiliation PDF')
    jobs['gap-3d4856c630d6'] = 'https://arxiv.org/html/2510.01173v1'
    decisions = maintainer_decisions(all_candidates, {c['candidate_id'] for c in approved})
    additions = {name: [] for name in ('papers.csv', 'paper_taxonomy.csv', 'author_institution_mappings.csv',
        'institutions.csv', 'institution_locations.csv', 'institution_hierarchy.csv', 'venue_aliases.csv',
        'review_decisions.csv', 'paper_exclusions.csv', 'institution_audit_log.csv', 'institution_location_review.csv')}
    changes = []
    aliases = read_venue_aliases()
    for name, acronym, track in [('Medical Image Computing and Computer Assisted Intervention', 'MICCAI', 'main'),
                                 ('Multimedia Evaluation Workshop', 'MediaEval', 'workshops')]:
        alias = {'alias': name, 'venue_id': 'venue:' + acronym.lower(), 'venue_name': name,
                 'venue_acronym': acronym, 'venue_type': 'conference', 'venue_track': track,
                 'review_status': 'confirmed', 'notes': 'Official proceedings verified for approved gap migration 2026-10-03.'}
        if not any(r['venue_name'] == name for r in aliases):
            additions['venue_aliases.csv'].append(shaped('venue_aliases.csv', alias))
            aliases.append(alias)
    registry = rows('institutions.csv')
    by_name = {r['canonical_name']: r for r in registry if r['institution_status'] == 'active'}
    active_by_id = {r['institution_id']: r for r in by_name.values()}
    for alias in rows('institution_aliases.csv'):
        if alias['review_status'] == 'confirmed' and alias['institution_id'] in active_by_id:
            by_name.setdefault(alias['alias_name'], active_by_id[alias['institution_id']])
    inst_checks = []
    location_evidence = {}
    new_locations_by_id = {}
    coordinate_ids = {'New Jersey Institute of Technology': 'Q3272013', 'Old Dominion University': 'Q1474100', 'University of Vigo': 'Q666916'}
    for inst in evidence['new_institutions']:
        name = inst['canonical_name']
        equivalent = [r for r in registry if audit.normalize(r['canonical_name']) == audit.normalize(name)]
        alias_matches = [r for r in rows('institution_aliases.csv') if audit.normalize(r['alias_name']) == audit.normalize(name)]
        if equivalent or alias_matches:
            raise ValueError('New institution requires reconciliation: ' + name)
        ident = 'institution:' + digest(name)
        by_name[name] = {**inst, 'institution_id': ident}
        inst_checks.append({'canonical_name': name, 'existing_exact_matches': equivalent, 'alias_matches': alias_matches,
                            'decision': 'New, primary-paper-supported entity; no existing institution merged.'})
    for inst in evidence['new_institutions']:
        name = inst['canonical_name']; ident = by_name[name]['institution_id']
        parent = by_name[inst['parent_name']]['institution_id'] if inst.get('parent_name') else ''
        additions['institutions.csv'].append(shaped('institutions.csv', {**inst, 'institution_id': ident,
            'parent_institution_id': parent, 'institution_status': 'active', 'public_display': 'self',
            'created_at': STAMP, 'updated_at': STAMP, 'created_by': CREATOR}))
        loc = {**inst, 'institution': name, 'normalized_institution': name.lower(), 'institution_id': ident,
               'location_id': 'location:' + digest(ident), 'coordinate_status': 'missing',
               'created_at': STAMP, 'updated_at': STAMP, 'created_by': CREATOR}
        if name in coordinate_ids:
            q = coordinate_ids[name]
            capture = next(s for s in manifest if s['url'].endswith('/' + q + '.json'))
            entity = json.loads(source_bytes(capture))['entities'][q]
            claims = [c for c in entity['claims']['P625'] if c['rank'] != 'deprecated']
            if len(claims) != 1:
                raise ValueError('Ambiguous institution coordinate: ' + name)
            coord = claims[0]['mainsnak']['datavalue']['value']
            loc.update(lat=coord['latitude'], lon=coord['longitude'], coordinate_status='known')
            location_evidence[ident] = {'name': name, 'source': capture['url'], 'capture': capture['raw_path'],
                'lat': coord['latitude'], 'lon': coord['longitude'], 'precision': coord['precision'],
                'decision': 'Reviewed ROR-linked institution entity coordinate. ROR city centroids were not used.'}
        new_locations_by_id[ident] = loc
        # The location registry contains confirmed coordinates only. Unknown
        # locations belong in the review queue, without placeholder coordinates.
        if loc['coordinate_status'] == 'known':
            additions['institution_locations.csv'].append(shaped('institution_locations.csv', loc))
        if parent:
            additions['institution_hierarchy.csv'].append(shaped('institution_hierarchy.csv', {
                'parent_institution_id': parent, 'child_institution_id': ident, 'relationship_type': 'affiliated_institute',
                'review_status': 'confirmed', 'evidence_source': 'Paper-time affiliation block',
                'evidence_url': jobs[inst['evidence_candidate']], 'notes': 'Explicit QCRI, Hamad Bin Khalifa University affiliation; distinct identities retained.'}))
    proposals = []
    venue_names = {'MICCAI': 'Medical Image Computing and Computer Assisted Intervention',
                   'MediaEval 2025 Workshop': 'Multimedia Evaluation Workshop',
                   'NDSS': 'Network and Distributed System Security Symposium'}
    for c in approved:
        c = dict(c)
        if c['title'].startswith('AdaParse'):
            c['doi'] = '10.1109/TIFS.2026.3671095'
        types = c['candidate_research_types']
        if c['title'].startswith('PRPO:'):
            types = ['method', 'dataset']
        scopes = c['candidate_image_scopes'] or ['fully_generated']
        publication = 'preprint' if c['venue'] == 'arXiv' else ('journal' if c['venue'] in ('Journal of Image and Graphics', 'IEEE Transactions on Information Forensics and Security') else 'conference')
        draft = normalize_paper_draft({**c, 'year': str(c['year']), 'venue': venue_names.get(c['venue'], c['venue']),
            'paper_url': c['official_url'] if publication != 'preprint' else '',
            'tasks': c['candidate_tasks'], 'image_scopes': scopes, 'research_types': types,
            'abstract': primary.get(audit.normalize(c['title']), {}).get('abstract', c.get('abstract', '')),
            'publication_type': publication, 'source_database': 'manual', 'scope_status': 'in_scope',
            'review_status': 'reviewed'})
        # Resolve newly approved venues with the same registry operation as existing venues.
        draft = canonicalize_record(draft, aliases=aliases)
        details = publication_details(c)
        source = 'Primary-source review 2026-10-03: ' + c['official_url'] + '; affiliation source: ' + jobs[c['candidate_id']]
        if details:
            source += '; publication details: ' + json.dumps(details, ensure_ascii=False)
        if c['title'].startswith('AdaParse'):
            source += '; DOI 10.1109/TIFS.2026.3671095 confirmed by maintainer; passive hyperparameter inference approved as source attribution.'
        if c['candidate_id'] in evidence['author_order_notes']:
            source += '; ' + evidence['author_order_notes'][c['candidate_id']]
        paper_id = 'curated:' + digest(normalized_title_year_key(draft))
        row = shaped('papers.csv', {**draft, 'paper_id': paper_id, 'metadata_source': source,
                                   'created_at': STAMP, 'updated_at': STAMP})
        proposal = {**row, 'candidate_id': c['candidate_id'], 'method_name': c.get('method_name', ''),
                    'publication_details': details, 'affiliation_source': jobs[c['candidate_id']],
                    'affiliation_review': evidence['papers'][c['candidate_id']]}
        proposals.append(proposal)
        additions['papers.csv'].append(row)
        rationale = c['scope_reason']
        if c['title'].startswith('PRPO:'):
            rationale = 'PRPO introduces DF-R5 with DDIM, PixArt-alpha, Stable Diffusion 2.1, SiT and StyleGAN3: independent generated-image detection method and dataset.'
        if c['title'].startswith('AdaParse'):
            rationale = 'Passive inference of source-generator hyperparameters from already generated images; no active fingerprint embedding. Maintainer accepts fine-grained reverse engineering as source attribution.'
        if c['title'].startswith('Beyond Visual Forensics'):
            rationale = 'Paired authenticity benchmark and analysis of image-fixed metadata swaps. Generated medical edits are in scope because the target is image authenticity, not diagnosis.'
        tax = {**row, 'taxonomy_id': 'paper_id:' + paper_id, 'taxonomy_status': 'reviewed', 'audited_at': STAMP}
        for dim in DIMENSIONS:
            tax.update({dim + '_status': 'reviewed', dim + '_review_reason': 'Maintainer decision 2026-10-03',
                        dim + '_evidence_tier': 'primary_full_text' if evidence['papers'][c['candidate_id']] else 'primary_abstract',
                        dim + '_evidence_source': c['official_url'], dim + '_evidence_excerpt': rationale})
        additions['paper_taxonomy.csv'].append(shaped('paper_taxonomy.csv', tax))
        for order, (name, positions, raw) in enumerate(evidence['papers'][c['candidate_id']], 1):
            inst = by_name[name]
            author_names = [c['authors'][i - 1] for i in positions]
            mapping = {**row, 'mapping_id': 'mapping:' + digest(paper_id + ':' + str(order)),
                       'institution': inst['canonical_name'], 'institution_id': inst['institution_id'],
                       'institution_authors': '; '.join(author_names), 'author_order': ';'.join(map(str, positions)),
                       'affiliation_order': order, 'raw_affiliation': raw, 'provenance_source': jobs[c['candidate_id']],
                       'mapping_status': 'active'}
            additions['author_institution_mappings.csv'].append(shaped('author_institution_mappings.csv', mapping))
            new_loc = new_locations_by_id.get(inst['institution_id'])
            if new_loc and new_loc['coordinate_status'] == 'missing':
                additions['institution_location_review.csv'].append(shaped('institution_location_review.csv', {
                    'institution': name, 'canonical_institution_name': name, 'institution_id': inst['institution_id'],
                    'related_paper_id': paper_id, 'title': row['title'], 'year': row['year'], 'doi': row['doi'],
                    'institution_authors': mapping['institution_authors'], 'raw_affiliation': raw,
                    'evidence_source': 'Paper-time affiliation; coordinates unverified', 'evidence_url': jobs[c['candidate_id']],
                    'suggested_city': new_loc['city'], 'suggested_country': new_loc['country'],
                    'review_status': 'pending_review', 'location_status': 'needs_coordinate_review', 'coordinate_status': 'missing',
                    'created_at': STAMP, 'updated_at': STAMP}))
        if c['candidate_id'] in evidence['unresolved']:
            for author in c['authors']:
                additions['institution_audit_log.csv'].append(shaped('institution_audit_log.csv', {
                    'audit_id': 'institution-audit:' + digest(paper_id + author), 'action': 'author_affiliation_review',
                    'paper_id': paper_id, 'affected_authors': author, 'evidence_source': 'Official author list; inaccessible PDF',
                    'evidence_url': c['official_url'], 'confirmation_text': json.dumps({'status': 'unresolved'}),
                    'review_note': evidence['unresolved'][c['candidate_id']], 'created_at': STAMP, 'created_by': CREATOR}))
    # Preserve identities and prior bibliography; change only the twelve approved rows.
    curated = {r['paper_id']: r for r in rows('papers.csv')}
    for c in all_candidates:
        if c['status'] != 'EXISTING_METADATA_UPDATE':
            continue
        old = curated[c['existing_paper_id']]; proposed = c['proposed_metadata']
        new = {**old, 'paper_url': proposed['formal_url'], 'title': canonical_paper_title(c['title']), 'updated_at': STAMP}
        for key in ('year', 'publication_type', 'doi'):
            if key in proposed:
                new[key] = str(proposed[key])
        if 'venue' in proposed:
            for key in ('venue_id', 'venue_name', 'venue_acronym', 'venue_type', 'venue_track', 'raw_venue'):
                new[key] = ''
            new['venue'] = proposed['venue']
        if 'authors' in proposed:
            new['authors'] = '; '.join(proposed['authors'])
        # arXiv identifiers remain in arxiv_id; they are not formal-publication DOIs.
        if new['doi'].lower().startswith('10.48550/arxiv.'):
            new['doi'] = ''
        new = canonicalize_record(new, aliases=aliases)
        new['metadata_source'] = ('Primary-source review 2026-10-03: ' + proposed['formal_url']
            + '; approved publication details: ' + json.dumps(proposed, ensure_ascii=False)
            + '; previous publication URL: ' + old['paper_url'] + '; previous year: ' + old['year']
            + '; previous metadata source: ' + old['metadata_source'])
        if 'authors' in proposed:
            new['metadata_source'] += '; previous author rendering: ' + old['authors']
        changes.append({'file': 'papers.csv', 'key': 'paper_id', 'identity': old['paper_id'],
                        'before': old, 'after': shaped('papers.csv', new), 'candidate_id': c['candidate_id']})
        for name, key in [('paper_taxonomy.csv', 'taxonomy_id'), ('author_institution_mappings.csv', 'mapping_id')]:
            for previous in rows(name):
                if previous['paper_id'] != old['paper_id']:
                    continue
                current = {**previous, **{k: str(new[k]) for k in ('title', 'year', 'doi')}}
                if name == 'author_institution_mappings.csv' and 'authors' in proposed:
                    rendered = {audit.author_name(n): n for n in proposed['authors']}
                    current['institution_authors'] = '; '.join(rendered.get(audit.author_name(n), n.strip()) for n in previous['institution_authors'].split(';'))
                if current != previous:
                    if 'updated_at' in current:
                        current['updated_at'] = STAMP
                    changes.append({'file': name, 'key': key, 'identity': previous[key], 'before': previous, 'after': current})
    by_candidate = {c['candidate_id']: c for c in all_candidates}
    for decision in decisions:
        if decision['decision'] == 'APPROVE_ADD':
            continue
        c = by_candidate[decision['candidate_id']]
        note = decision['decision'] + ': ' + decision['note'] + ' Sources: ' + '; '.join(decision['source_urls'])
        additions['review_decisions.csv'].append(shaped('review_decisions.csv', {
            'decision_id': 'review:' + digest(c['candidate_id'] + STAMP), 'review_queue': 'other', 'target_type': 'paper',
            'title': c['title'], 'year': c['year'], 'doi': c['doi'],
            'action': 'exclude_paper_scope' if decision['decision'] == 'EXCLUDE_OUT_OF_SCOPE' else 'unresolved',
            'review_note': note, 'created_at': STAMP, 'updated_at': STAMP, 'created_by': CREATOR}))
        if decision['decision'] == 'EXCLUDE_OUT_OF_SCOPE':
            additions['paper_exclusions.csv'].append(shaped('paper_exclusions.csv', {
                'exclusion_id': 'exclusion:' + digest(c['candidate_id']), 'title': c['title'], 'year': c['year'], 'doi': c['doi'],
                'reason': 'out_of_scope', 'review_note': note, 'excluded_from_public_preview': 'true',
                'excluded_from_map': 'true', 'is_active': 'true', 'created_at': STAMP, 'created_by': CREATOR,
                'source_database': 'manual', 'metadata_source': c['official_url']}))
    checks = live_reconciliation(proposals)
    if any(c['outcome'] != 'ADD_NEW' for c in checks):
        # Never force 17. A changed live identity needs an explicitly reconciled
        # row-level update plan instead of blindly appending the old proposal.
        save('live_deduplication.json', checks)
        raise ValueError('Approved candidate now exists: convert its plan to the reported stable identity before applying.')
    save('live_deduplication.json', checks)
    save('institution_identity_checks.json', inst_checks)
    save('location_evidence.json', location_evidence)
    save('maintainer_decisions.json', decisions)
    save('plan.json', {'prepared_at': STAMP, 'papers': proposals, 'additions': additions, 'updates': changes,
        'curated_input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / 'data/curated').glob('*.csv')}})
    print(json.dumps({'additions': {k: len(v) for k, v in additions.items()}, 'updated_rows': len(changes)}, indent=2))


def csv_delta_bytes(original, additions, updates):
    """Retain untouched CSV rows byte-for-byte, including mixed line endings."""
    text = original.decode('utf-8')
    lines = text.splitlines(keepends=True)
    reader = csv.DictReader(io.StringIO(text, newline=''))
    fields = reader.fieldnames
    previous_line = reader.line_num
    output = [''.join(lines[:previous_line])]
    pending = {(u['key'], u['identity']): u for u in updates}

    def serialize(row, newline):
        stream = io.StringIO(newline='')
        csv.DictWriter(stream, fieldnames=fields, lineterminator=newline).writerow(row)
        return stream.getvalue()

    for row in reader:
        chunk = ''.join(lines[previous_line:reader.line_num])
        previous_line = reader.line_num
        match = next((k for k in pending if row.get(k[0]) == k[1]), None)
        if match is not None:
            change = pending.pop(match)
            if row != change['before']:
                raise ValueError('Curated row changed after review: ' + match[1])
            chunk = serialize(change['after'], '\r\n' if chunk.endswith('\r\n') else '\n')
        output.append(chunk)
    if pending:
        raise ValueError('Update identities missing from CSV: ' + str(list(pending)))
    newline = '\r\n' if lines[0].endswith('\r\n') else '\n'
    output.extend(serialize(row, newline) for row in additions)
    return ''.join(output).encode('utf-8')


def write_delta(name, additions, updates):
    path = ROOT / 'data/curated' / name
    path.write_bytes(csv_delta_bytes(path.read_bytes(), additions, updates))


def apply():
    if (OUT / 'insertion.json').exists():
        raise ValueError('Already applied; refusing duplicate writes.')
    plan = read(OUT / 'plan.json')
    for name, expected in plan['curated_input_sha256'].items():
        if hashlib.sha256((ROOT / 'data/curated' / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Live curated input changed: ' + name)
    checks = live_reconciliation(plan['papers'])
    save('live_deduplication.json', checks)
    if any(c['outcome'] != 'ADD_NEW' for c in checks):
        raise ValueError('Live candidate now exists. Reconcile to metadata update; no writes performed.')
    baseline = read(OUT / 'baseline.json')
    for name, expected in baseline['frozen_sha256'].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Frozen artifact changed: ' + name)
    # Every input is checked before the first write. Only named rows are changed.
    for name, additions in plan['additions'].items():
        updates = [u for u in plan['updates'] if u['file'] == name]
        if additions or updates:
            write_delta(name, additions, updates)
    ledger_path = AUDIT / 'candidates.json'
    ledger = read(ledger_path)
    save('discovery_snapshot.json', ledger)
    decisions = {d['candidate_id']: d for d in read(OUT / 'maintainer_decisions.json')}
    added_ids = {p['candidate_id']: p['paper_id'] for p in plan['papers']}
    updated_ids = {u['candidate_id']: u['identity'] for u in plan['updates'] if u['file'] == 'papers.csv'}
    for c in ledger['works']:
        if c['candidate_id'] in decisions:
            c['maintainer_decision'] = decisions[c['candidate_id']]
        if c['candidate_id'] in added_ids or c['candidate_id'] in updated_ids:
            c['migration_outcome'] = {'applied_at': STAMP,
                'action': 'ADD_NEW' if c['candidate_id'] in added_ids else 'UPDATE_METADATA',
                'paper_id': added_ids.get(c['candidate_id'], updated_ids.get(c['candidate_id'])),
                'receipt': str((OUT / 'insertion.json').relative_to(ROOT))}
    # Original statuses, evidence, counts and frozen_encounters remain intact.
    ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n')
    save('insertion.json', {'applied_at': STAMP, 'paper_ids': [p['paper_id'] for p in plan['papers']],
        'added_rows': {k: len(v) for k, v in plan['additions'].items()},
        'metadata_update_ids': [u['identity'] for u in plan['updates'] if u['file'] == 'papers.csv'],
        'converted_to_existing_updates': [], 'frozen_status': '7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA'})
    print('Curated migration applied. Run the existing public exporter and validation suite.')


def validation_payload():
    """Recompute counts and separate authorized changes from integrity failures."""
    baseline = read(OUT / 'baseline.json')
    plan = read(OUT / 'plan.json')
    public = read(ROOT / 'web/data/public_preview_papers.json')['records']
    maps = read(ROOT / 'web/data/public_preview_map_data.json')['records']
    counts = {'public_papers': len(public),
              'formally_published': sum(p.get('publication_type') in ('conference', 'journal', 'book') for p in public),
              'mapped_papers': sum(bool(p.get('has_map_location')) for p in public), 'relationships': len(maps),
              'tasks': dict(Counter(v for p in public for v in p['tasks'])),
              'research_types': dict(Counter(v for p in public for v in p['research_types']))}
    errors = []
    duplicate_checks = {}
    for field, normalize in [('doi', audit.doi), ('arxiv_id', audit.arxiv), ('title', audit.normalize)]:
        values = Counter(normalize(p.get(field, '')) for p in public if normalize(p.get(field, '')))
        duplicates = {value: n for value, n in values.items() if n > 1}
        duplicate_checks[field] = duplicates
        if duplicates:
            errors.append('Duplicate public ' + field)
    unexpected_rows = []
    for name, previous in baseline['curated_rows'].items():
        expected = [dict(r) for r in previous]
        for change in plan['updates']:
            if change['file'] == name:
                index = next(i for i, r in enumerate(expected) if r[change['key']] == change['identity'])
                if expected[index] != change['before']:
                    errors.append('Update baseline differs: ' + change['identity'])
                expected[index] = change['after']
        expected.extend(plan['additions'].get(name, []))
        if rows(name) != expected:
            unexpected_rows.append(name)
    if unexpected_rows:
        errors.append('Unexpected curated row changes: ' + ', '.join(unexpected_rows))
    allowed = {'data/curated/' + n for n, additions in plan['additions'].items()
               if additions or any(u['file'] == n for u in plan['updates'])}
    allowed |= {'web/data/public_preview_map_data.json', 'web/data/public_preview_papers.json'}
    changed = [path for path, sha in baseline['protected_105'].items()
               if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != sha]
    expected_changed = sorted(set(changed) & allowed)
    unexpected_changed = sorted(set(changed) - allowed)
    frozen_changed = [path for path, sha in baseline['frozen_sha256'].items()
                      if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != sha]
    if unexpected_changed or frozen_changed:
        errors.append('Protected or frozen integrity violation')
    by_id = {p['paper_id']: p for p in public if p.get('paper_id')}
    frozen = baseline['frozen_mirror_public']
    if by_id.get(frozen['paper_id']) != frozen:
        errors.append('Frozen MIRROR public record changed')
    added_ids = {p['paper_id'] for p in plan['papers']}
    updated_ids = {u['identity'] for u in plan['updates'] if u['file'] == 'papers.csv'}
    historical = read(OUT / 'predecessor_623_manifest.json')['web/data/public_preview_papers.json']
    previous_bytes = gzip.decompress((OUT / historical['archive']).read_bytes())
    if hashlib.sha256(previous_bytes).hexdigest() != baseline['tracked_sha256']['web/data/public_preview_papers.json']:
        raise ValueError('Pre-migration public snapshot checksum mismatch')
    old_public = json.loads(previous_bytes)['records']
    def key(p):
        return p.get('paper_id') or p.get('openalex_url') or audit.normalize(p['title'])
    old = {key(p): p for p in old_public}; new = {key(p): p for p in public}
    actual_added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    unrelated_public_changes = {ident: [k for k in set(old[ident]) | set(new[ident]) if old[ident].get(k) != new[ident].get(k)]
        for ident in set(old) & set(new) if ident not in updated_ids and old[ident] != new[ident]}
    if set(actual_added) != added_ids or removed or unrelated_public_changes:
        errors.append('Unexpected public identity or record change')
    affiliations = []
    for proposal in plan['papers']:
        p = by_id[proposal['paper_id']]
        mapped_authors = p.get('author_affiliation_counts', {}).get('mapped', 0)
        unresolved = [a['name'] for a in p['authors'] if a.get('affiliation_status') == 'unresolved']
        expected_institutions = {m['institution_id'] for m in plan['additions']['author_institution_mappings.csv'] if m['paper_id'] == p['paper_id']}
        plotted = {r['institution_id'] for r in maps if r.get('paper_id') == p['paper_id']}
        affiliations.append({'candidate_id': proposal['candidate_id'], 'paper_id': p['paper_id'], 'title': p['title'],
            'authors': len(p['authors']), 'authors_with_verified_affiliation': mapped_authors,
            'unresolved_authors': unresolved, 'affiliation_complete': p.get('affiliation_complete'),
            'verified_institutions': len(expected_institutions), 'plotted_institutions': len(plotted),
            'map_coverage': 'unmapped' if not plotted else 'fully_mapped' if plotted == expected_institutions else 'partially_mapped',
            'has_map_location': p['has_map_location']})
    payload = {'before': baseline['counts'], 'after': counts, 'actual_new_identities': actual_added,
        'removed_identities': removed, 'metadata_updated_identities': sorted(updated_ids),
        'duplicates': duplicate_checks, 'affiliations': affiliations,
        'expected_changed_protected_files': expected_changed,
        'unexpected_changed_protected_files': unexpected_changed, 'frozen_changed_files': frozen_changed,
        'frozen_files_checked': len(baseline['frozen_sha256']), 'protected_files_checked': len(baseline['protected_105']),
        'unexpected_curated_files': unexpected_rows, 'unrelated_public_changes': unrelated_public_changes,
        'errors': errors}
    return payload


def validate():
    payload = validation_payload()
    save('validation.json', payload)
    print(json.dumps({k: v for k, v in payload.items() if k not in ('affiliations', 'actual_new_identities', 'metadata_updated_identities')}, indent=2))
    return not payload['errors']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'apply', 'validate'])
    args = parser.parse_args()
    result = {'prepare': prepare, 'apply': apply, 'validate': validate}[args.command]()
    if result is False:
        raise SystemExit(1)
