#!/usr/bin/env python3
"""Audit the ten reviewed additions without modifying curated/manual sources."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

try:
    from .paper_links import resolve_public_links
    from .paper_exclusions import build_active_exclusion_index, record_is_excluded, all_identity_keys
except ImportError:
    from paper_links import resolve_public_links
    from paper_exclusions import build_active_exclusion_index, record_is_excluded, all_identity_keys

ROOT = Path(__file__).resolve().parents[1]
LEDGER = Path('data/manual/primary_paper_curation_2026_09_08.json')
BASELINE = Path('data/processed/primary_curation_baseline_2026_09_08.json')
OUTPUT = Path('docs/primary_paper_curation_2026_09_08')
DIMENSIONS = ('tasks', 'image_scopes', 'research_types')


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def digest(row):
    return hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def strict_regression(root=ROOT):
    baseline = json.loads((root / BASELINE).read_text())
    targets = set(baseline['target_paper_ids'])
    appendable = {'author_institution_mappings.csv', 'institutions.csv',
                  'institution_locations.csv', 'institution_hierarchy.csv',
                  'institution_audit_log.csv', 'institution_location_audit_log.csv',
                  'institution_location_review.csv'}
    reports = {'data/manual/key_paper_coverage_report.csv',
               'data/manual/missing_author_mappings_report.csv'}
    changes, additions, preserved = [], {}, 0
    for relative, before in baseline['files'].items():
        path = root / relative
        if relative in reports:
            continue
        if not path.exists():
            changes.append(relative + ': removed')
            continue
        if 'rows' not in before:
            if hashlib.sha256(path.read_bytes()).hexdigest() != before['sha256']:
                changes.append(relative + ': bytes changed')
            continue
        rows = read_csv(path)
        for i, old in enumerate(before['rows']):
            if path.name in {'papers.csv', 'paper_taxonomy.csv'} and old['paper_id'] in targets:
                continue
            if i >= len(rows) or digest(rows[i]) != old['row_sha256']:
                changes.append(f'{relative}: pre-existing row {i + 2} changed/removed')
            else:
                preserved += 1
        extra = rows[len(before['rows']):]
        if extra and path.name not in appendable:
            changes.append(relative + ': unexpected appended records')
        if extra:
            additions[relative] = len(extra)
        if path.name == 'author_institution_mappings.csv':
            if any(r['paper_id'] not in targets for r in extra):
                changes.append(relative + ': appended relationship for older paper')
    return {'pre_existing_changes': changes, 'pre_existing_rows_preserved': preserved,
            'appended_rows': additions}


def build_audit(root=ROOT):
    followup = root / 'data/processed/systematic_tier1_2026_09'
    if (followup / 'insertion.json').exists():
        # This report documents the completed ten-paper pass, before Tier 1.
        # Its frozen input snapshot is independently checked by the Tier 1 audit.
        root = followup / 'baseline'
    ledger = json.loads((root / LEDGER).read_text())
    decisions = ledger['papers']
    baseline = json.loads((root / BASELINE).read_text())
    ids = {d['paper_id'] for d in decisions}
    if len(decisions) != 10 or len(ids) != 10 or ids != set(baseline['target_paper_ids']):
        raise ValueError('Curation must cover exactly the original ten identities')
    integrity = strict_regression(root)
    if integrity['pre_existing_changes']:
        raise ValueError('\n'.join(integrity['pre_existing_changes']))
    papers = {r['paper_id']: r for r in read_csv(root / 'data/curated/papers.csv')}
    exclusions = read_csv(root / 'data/curated/paper_exclusions.csv')
    exclusion_index = build_active_exclusion_index(exclusions)
    excluded_ids = {pid for pid in ids if record_is_excluded(papers[pid], exclusion_index)}
    taxonomy = {r['paper_id']: r for r in read_csv(root / 'data/curated/paper_taxonomy.csv') if r['paper_id']}
    mappings = read_csv(root / 'data/curated/author_institution_mappings.csv')
    institutions = read_csv(root / 'data/curated/institutions.csv')
    locations = read_csv(root / 'data/curated/institution_locations.csv')
    hierarchy = read_csv(root / 'data/curated/institution_hierarchy.csv')
    pub = json.loads((root / 'web/data/public_preview_papers.json').read_text())['records']
    markers = json.loads((root / 'web/data/public_preview_map_data.json').read_text())['records']
    if len(pub) != 623 - len(excluded_ids):
        raise ValueError('Public count differs from baseline minus existing excluded identities')
    integrity['pre_existing_public_changes'] = []
    integrity['pre_existing_public_records_preserved'] = {}
    for relative, old_rows in baseline['public_files'].items():
        current_rows = pub if relative.endswith('papers.json') else markers
        lookup = {r.get('id') or r.get('paper_id') or r.get('doi') or r['title']: r for r in current_rows}
        protected = [r for r in old_rows if r['paper_id'] not in ids]
        for old in protected:
            if old['record_key'] not in lookup or digest(lookup[old['record_key']]) != old['row_sha256']:
                integrity['pre_existing_public_changes'].append(relative + ': ' + old['record_key'])
        integrity['pre_existing_public_records_preserved'][relative] = len(protected)
    if integrity['pre_existing_public_changes']:
        raise ValueError('Unintended change to protected public records')
    strong_ids = {}
    for p in pub:
        for key in all_identity_keys(p):
            if not key.startswith('title_year:'):
                strong_ids.setdefault(key, []).append(p['title'])
    integrity['strong_identifier_duplicates'] = {k: v for k, v in strong_ids.items() if len(v) > 1}
    if integrity['strong_identifier_duplicates']:
        raise ValueError('Duplicate strong identifiers in public bibliography')
    result = []
    for d in decisions:
        p, t = papers[d['paper_id']], taxonomy.get(d['paper_id'])
        excluded = d['paper_id'] in excluded_ids
        matches = [r for r in pub if r.get('paper_id') == d['paper_id']]
        if len(matches) != (0 if excluded else 1) or (excluded and t is not None):
            raise ValueError(f'Public/excluded identity mismatch: {d["paper_id"]}')
        public = matches[0] if matches else None
        for key, value in d['bibliography_overrides'].items():
            if p[key] != value:
                raise ValueError(f'Bibliography decision drift: {d["paper_id"]} {key}')
        for dimension in DIMENSIONS:
            if p[dimension] != ';'.join(d[dimension]):
                raise ValueError(f'Curated taxonomy drift: {d["paper_id"]} {dimension}')
            if not excluded and (t[dimension] != ';'.join(d[dimension])
                    or public[dimension] != d[dimension]
                    or t[dimension + '_status'] != d['taxonomy_status']
                    or not t[dimension + '_evidence_source']
                    or t[dimension + '_evidence_excerpt'] != d['taxonomy_evidence'][dimension]):
                raise ValueError(f'Taxonomy/evidence drift: {d["paper_id"]} {dimension}')
        if any(p[k] != d[k] for k in ('curation_status', 'review_status')):
            raise ValueError('Review state differs from individually reviewed decision')
        if not excluded:
            for field in ('title', 'doi', 'arxiv_id', 'openalex_url', 'publication_type',
                          'venue_id', 'raw_venue', 'metadata_source', 'curation_status', 'review_status'):
                if public.get(field, '') != p.get(field, ''):
                    raise ValueError(f'Public metadata drift: {d["paper_id"]} {field}')
            if public.get('year') != int(p['year']):
                raise ValueError('Public publication year drift')
            links = resolve_public_links(p)
            for field in ('primary_url', 'arxiv_url', 'formal_url'):
                if public.get(field, '') != links[field]:
                    raise ValueError(f'Public publication link drift: {d["paper_id"]} {field}')
            if [a['name'] for a in public['authors']] != p['authors'].split('; '):
                raise ValueError('Public author order drift')
            expected_status = 'Verified' if d['review_status'] == 'reviewed' else 'Needs review'
            if public.get('metadata_status', {}).get('overall') != expected_status:
                raise ValueError('Public Paper Details review status drift')
        if d['overall_state'] == 'fully_curated' and d['unresolved_fields']:
            raise ValueError('Fully curated record has unresolved fields')
        actual = [r for r in mappings if r['paper_id'] == d['paper_id'] and r['mapping_status'] == 'active']
        expected_pairs = {(a, f['institution']) for f in d['affiliations'] for a in f['authors']}
        actual_pairs = {(a.strip(), r['institution']) for r in actual for a in r['institution_authors'].split(';')}
        if actual_pairs != expected_pairs or len(actual) != len(d['affiliations']):
            raise ValueError(f'Author-specific relationship drift: {d["paper_id"]}')
        if not excluded:
            exported_pairs = {(a, r['institution']) for r in public.get('curated_mappings', [])
                              for a in r['institution_authors']}
            if exported_pairs != expected_pairs or public.get('affiliation_review_state') != 'curated':
                raise ValueError('Public verified affiliation relationships drift')
            if any(a.get('affiliation_status') != 'mapped' or not a.get('affiliation_review', {}).get('evidence_url')
                   for a in public['authors']):
                raise ValueError('Public author-specific evidence drift')
        author_names = set(p['authors'].split('; '))
        if {a for a, _ in expected_pairs} != author_names:
            raise ValueError('Full author-list coverage drift')
        m = [r for r in markers if r.get('paper_id') == d['paper_id']]
        if excluded and m:
            raise ValueError('An existing exclusion was bypassed by public markers')
        mapped_ids = {r['institution_id'] for r in actual}
        if any(r['institution_id'] not in mapped_ids for r in m):
            raise ValueError('Marker without verified paper-institution relationship')
        for r in m:
            if not any(loc['institution_id'] == r['institution_id'] and loc['coordinate_status'] == 'known'
                       for loc in locations):
                raise ValueError('Marker without reviewed coordinates')
        pending = sorted({r['institution'] for r in actual if not any(
            loc['institution_id'] == r['institution_id'] and loc['coordinate_status'] == 'known'
            for loc in locations)})
        matched_exclusions = [r for r in exclusions if record_is_excluded(p, build_active_exclusion_index([r]))]
        match_keys = sorted({k for r in matched_exclusions for k in
                            set(all_identity_keys(r)) & set(all_identity_keys(p)) if not k.startswith('title_year:')})
        result.append(dict(paper_id=p['paper_id'], title=p['title'],
            curated_presence=True,
            public_status='excluded' if excluded else 'included',
            membership_state='CURATED_BUT_EXCLUDED' if excluded else 'CURATED_AND_PUBLIC',
            existing_exclusion_ids='; '.join(r['exclusion_id'] for r in matched_exclusions),
            exclusion_reason='; '.join(r['reason'] for r in matched_exclusions),
            exclusion_effective_date='; '.join(r['created_at'] for r in matched_exclusions),
            exclusion_match_identity='; '.join(match_keys),
            exclusion_doi='; '.join(r['doi'] for r in matched_exclusions),
            doi=p['doi'], arxiv_id=p['arxiv_id'], openalex_url=p['openalex_url'],
            bibliography_status=d['bibliography_status'], publication_status=d['publication_status'],
            taxonomy_status=d['taxonomy_status'], affiliation_status=d['affiliation_status'],
            location_status='needs_review' if pending else 'reviewed',
            **{k: p[k] for k in DIMENSIONS},
            verified_institutions='; '.join(f['institution'] for f in d['affiliations']),
            verified_institution_count=len(d['affiliations']),
            verified_author_institution_relationships=len(expected_pairs), marker_count=len(m),
            map_marker_status='excluded' if excluded else ('marker_bearing' if m else 'markerless'),
            primary_evidence_urls='; '.join(d['primary_evidence_urls']),
            pending_locations='; '.join(pending), unresolved_fields=' | '.join(d['unresolved_fields']),
            unresolved_reason=d['bibliographic_evidence'] if d['bibliography_status'] != 'reviewed' else ' | '.join(d['unresolved_fields']),
            overall_state=d['overall_state'], curation_status=p['curation_status'], review_status=p['review_status']))
    summary = {k: sum(r[field] == value for r in result) for k, field, value in (
        ('bibliography_verified', 'bibliography_status', 'reviewed'),
        ('taxonomy_reviewed', 'taxonomy_status', 'reviewed'),
        ('affiliation_reviewed', 'affiliation_status', 'reviewed'),
        ('fully_curated', 'overall_state', 'fully_curated'),
        ('marker_bearing', 'map_marker_status', 'marker_bearing'))}
    summary.update(public_papers=len(pub), public_mapped_papers=sum(bool(r.get('has_map_location')) for r in pub),
                   published_only=sum(r['publication_type'] in {'conference', 'journal', 'book'} for r in pub),
                   before_counts=baseline['before_counts'],
                   markerless=[r['title'] for r in result if r['map_marker_status'] == 'markerless'],
                   excluded=[r['title'] for r in result if r['public_status'] == 'excluded'],
                   new_institutions=[r['name'] for r in ledger['institutions']],
                   new_aliases=0, new_hierarchy_relationships=sum(bool(r.get('parent')) for r in ledger['institutions']))
    return {'summary': summary, 'integrity': integrity, 'papers': result}


def render(report):
    rows = report['papers']
    csvout = io.StringIO(newline='')
    writer = csv.DictWriter(csvout, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    lines = ['# Primary-source curation of ten reconciliation additions — 2026-09-08', '',
        'This is the current curation audit. The earlier key-paper reconciliation report is a historical snapshot of addition-time review state. No checklist identities or ambiguous cases were re-adjudicated.', '',
        'Bibliography, taxonomy, author affiliation and location are reviewed independently. A reviewed affiliation means the author–institution relationship is supported; it does not imply a verified coordinate. Campus/headquarters points are representative institutional geography, not personal work-location claims. Full curation requires no remaining material uncertainty.', '',
        'Verified OpenAlex identities revealed existing July 13 exclusions for Provenance, PLADA and FusionDetect. The earlier reconciliation missed those exclusions because the new rows lacked those identifiers. All ten authoritative rows and their reviewed taxonomy remain in papers.csv and the evidence ledger; the public-only taxonomy registry omits the three excluded identities. No exclusion decision was changed. Public membership and curation completeness are independent.', '',
        '| Title | Bibliography | Tasks | Image scopes | Research types | Verified institutions | Author–institution pairs | Markers | Public membership | Pending fields | Overall state |',
        '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        vals = [r[k] for k in ('title', 'publication_status', 'tasks', 'image_scopes', 'research_types',
                 'verified_institutions', 'verified_author_institution_relationships', 'marker_count', 'public_status', 'unresolved_fields', 'overall_state')]
        lines.append('| ' + ' | '.join(str(v).replace('|', '\\|') or '—' for v in vals) + ' |')
    lines += ['', '## Review counts', '', '```json', json.dumps(report['summary'], indent=2), '```', '',
              '## Strict regression audit', '', '```json', json.dumps(report['integrity'], indent=2), '```', '',
              '## Evidence and unresolved decisions', '']
    for r in rows:
        lines += [f'### {r["title"]}', '', f'Paper ID: `{r["paper_id"]}`. Bibliography: {r["bibliography_status"]}; taxonomy: {r["taxonomy_status"]}; affiliations: {r["affiliation_status"]}; locations: {r["location_status"]}.', '',
                  r['unresolved_reason'] or 'No remaining material curation uncertainty in inspected sources.', '',
                  'Public membership: ' + r['public_status'] + ('. Existing exclusions: ' + r['existing_exclusion_ids'] if r['existing_exclusion_ids'] else '') + '.', '',
                  ('Exclusion identity trace: curated ID `' + r['paper_id'] + '`; formal DOI `' + (r['doi'] or 'none established') + '`; arXiv `' + r['arxiv_id'] + '`; OpenAlex ' + r['openalex_url'] + '. Match: `' + r['exclusion_match_identity'] + '`; exclusion DOI `' + r['exclusion_doi'] + '`; reason `' + r['exclusion_reason'] + '`; effective ' + r['exclusion_effective_date'] + '. The unchanged exclusion predates this task.') if r['existing_exclusion_ids'] else '', '',
                  'Primary evidence: ' + ' · '.join(f'[source {i+1}]({u})' for i,u in enumerate(r['primary_evidence_urls'].split('; '))), '']
    lines += ['The field-specific rationales, exact author groupings, version notes, explicit code URLs, institution provenance and representative-location limitations are in `data/manual/primary_paper_curation_2026_09_08.json`. Full source PDFs and secondary/geocoding responses are cached separately under `data/raw/primary_curation_2026_09_08/`.', '',
              'Regenerate with `python3 scripts/report_primary_paper_curation.py`; verify without writes with `--check`. Run `--regression-only` before a refresh to check source preservation independently of public outputs.', '']
    return {'.csv': csvout.getvalue(), '.json': json.dumps(report, indent=2, ensure_ascii=False) + '\n', '.md': '\n'.join(lines)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--regression-only', action='store_true')
    args = parser.parse_args()
    if args.regression_only:
        result = strict_regression()
        print(json.dumps(result, indent=2))
        return int(bool(result['pre_existing_changes']))
    report = build_audit()
    for suffix, text in render(report).items():
        path = ROOT / (str(OUTPUT) + suffix)
        if args.check:
            if not path.exists() or path.read_text() != text:
                raise SystemExit(f'Stale primary curation audit: {path}')
        else:
            path.write_text(text)
    print(json.dumps(report['summary'], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
