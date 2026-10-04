#!/usr/bin/env python3
"""Read-only corpus comparison and isolated source capture for the October audit.

All writes are confined to this audit's raw directory. This never exports,
curates, merges identities, assigns final taxonomy, or changes manual data.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import difflib
from functools import lru_cache
import gzip
import hashlib
import html
import json
from pathlib import Path
import re
import unicodedata
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/raw/systematic_gap_audit_2026_10_02'
STATUSES = ('EXISTING_CURRENT', 'EXISTING_METADATA_UPDATE',
            'MISSING_HIGH_CONFIDENCE', 'MISSING_NEEDS_SCOPE_REVIEW',
            'DUPLICATE_VERSION', 'EXCLUDE_OUT_OF_SCOPE', 'AMBIGUOUS',
            'EXISTING_PENDING_FROZEN_NEURIPS_2026')
FROZEN_ARXIV = {'2605.31153', '2602.02222', '2605.08574', '2609.30982',
                '2605.27924', '2606.12671', '2609.30997'}
FROZEN_TITLES = {
    'beyondrealorfakeadualchannelauthenticityandreasoningprotocolforphotographicassessment'
}


@lru_cache(maxsize=50000)
def normalize(value):
    value = html.unescape(re.sub(r'<[^>]+>', '', str(value))).replace('&', ' and ')
    return ''.join(c for c in unicodedata.normalize('NFKD', value).casefold() if c.isalnum())


def doi(value):
    return re.sub(r'^https?://(?:dx\.)?doi.org/', '', str(value).strip().lower())


def arxiv(value):
    match = re.search(r'\d{4}\.\d{4,5}', str(value))
    return match[0] if match else ''


def author_name(value):
    """Compare name renderings without merging author identities."""
    if isinstance(value, dict):
        value = value.get('name', '')
    parts = str(value).split(',', 1)
    return normalize(' '.join(reversed(parts)) if len(parts) == 2 else value)


def read_json(path):
    return json.loads(path.read_text())


def write_json(name, value):
    target = OUT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


@lru_cache(maxsize=1)
def corpus():
    return read_json(ROOT / 'web/data/public_preview_papers.json')['records']


@lru_cache(maxsize=1)
def identity_layers():
    result = []
    for folder in ['data/curated', 'data/manual']:
        for path in sorted((ROOT / folder).glob('*.csv')):
            with path.open(encoding='utf-8-sig', newline='') as handle:
                for number, row in enumerate(csv.DictReader(handle), 2):
                    result.append((str(path.relative_to(ROOT)), number, row))
    return result


def compare(candidate):
    """Expose seven checks as evidence; fuzzy/acronym/author hits never merge."""
    papers = corpus()
    direct = {}
    for field, clean in [('doi', doi), ('arxiv_id', arxiv), ('title', normalize), ('paper_id', str)]:
        val = clean(candidate.get(field, ''))
        hits = []
        if val:
            for paper in papers:
                if clean(paper.get(field, '')) == val:
                    hits.append(paper.get('paper_id') or paper.get('openalex_url') or paper['title'])
        direct[field] = hits
    scored = [(difflib.SequenceMatcher(None, normalize(candidate['title']), normalize(p['title'])).ratio(), p) for p in papers]
    ranked = sorted(scored, key=lambda pair: pair[0], reverse=True)[:3]
    fuzzy = [{'title': p['title'], 'paper_id': p.get('paper_id', ''), 'score': round(score, 4)} for score, p in ranked]
    names = candidate.get('authors', [])
    if isinstance(names, str):
        names = names.split(';')
    surnames = {author_name(n) for n in names if n} - {''}
    author_year = []
    for p in papers:
        pn = p.get('authors', [])
        if isinstance(pn, str):
            pn = pn.split(';')
        overlap = surnames & {author_name(n) for n in pn}
        if overlap and abs(int(p.get('year') or 0) - int(candidate.get('year') or 0)) <= 1:
            author_year.append({'title': p['title'], 'paper_id': p.get('paper_id', ''), 'shared_authors': sorted(overlap)})
    method = candidate.get('method_name', '')
    acronym = [{'title': p['title'], 'paper_id': p.get('paper_id', '')} for p in papers if method and re.search(r'(?<!\w)' + re.escape(method) + r'(?!\w)', p['title'], re.I)]
    other_layers = []
    # Search all curated/manual identity layers, including exclusions and versions.
    for path, number, row in identity_layers():
        hits = []
        for field, clean in [('doi', doi), ('arxiv_id', arxiv), ('title', normalize)]:
            val = clean(candidate.get(field, ''))
            if val and any(clean(v) == val for k, v in row.items() if v and (field in k or field == 'title' and k == 'canonical_title')):
                hits.append(field)
        if hits:
            other_layers.append({'path': path, 'line': number, 'matched_on': hits})
    return {'exact_public': direct, 'acronym_matches': acronym, 'title_similarity_top3': fuzzy,
            'author_year_matches': author_year, 'curated_manual_matches': other_layers,
            'policy': 'Only exact reviewed identity evidence establishes identity; suggestions require human adjudication.'}


def fetch(url, label):
    """Cache original response bytes (gzip) and retrieval outcome without retry loops."""
    path = OUT / 'source_manifest.json'
    manifest = read_json(path) if path.exists() else []
    previous = next((r for r in manifest if r['url'] == url), None)
    if previous:
        return previous
    item = {'url': url, 'label': label, 'retrieved_at': datetime.now(timezone.utc).isoformat()}
    body = b''
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'AcademicLiteratureAudit/1.0 (public metadata; no credentials)'})
        with urllib.request.urlopen(request, timeout=35) as response:
            body = response.read()
            item.update(status=response.status, final_url=response.url, content_type=response.headers.get('Content-Type', ''))
    except urllib.error.HTTPError as error:
        body = error.read()
        item.update(status=error.code, error=str(error))
    except (urllib.error.URLError, TimeoutError) as error:
        item.update(status='NETWORK_ERROR', error=str(error))
    if body:
        name = 'sources/' + hashlib.sha256(url.encode()).hexdigest()[:20] + '.gz'
        target = OUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(gzip.compress(body, mtime=0))
        item.update(raw_path=str(target.relative_to(ROOT)), response_sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
    manifest.append(item)
    write_json('source_manifest.json', manifest)
    return item


def candidate_errors(payload):
    """Validate audit-only records without modifying any input or corpus data."""
    errors = []
    works = payload.get('works', [])
    all_records = works + payload.get('frozen_encounters', [])
    for field, normalizer in [('candidate_id', str), ('title', normalize),
                               ('doi', doi), ('arxiv_id', arxiv)]:
        seen = {}
        for c in all_records:
            value = normalizer(c.get(field, ''))
            if value and value in seen:
                errors.append('Duplicate ' + field + ': ' + value)
            if value:
                seen[value] = c.get('candidate_id')
    for c in all_records:
        cid = c.get('candidate_id', '<missing>')
        status = c.get('status')
        if not c.get('candidate_id') or status not in STATUSES:
            errors.append('Invalid identity/status: ' + cid)
        frozen = arxiv(c.get('arxiv_id')) in FROZEN_ARXIV or normalize(c.get('title')) in FROZEN_TITLES
        if frozen and status != 'EXISTING_PENDING_FROZEN_NEURIPS_2026':
            errors.append('Frozen work reclassified: ' + cid)
        if c in works and status == 'EXISTING_PENDING_FROZEN_NEURIPS_2026':
            errors.append('Frozen work must be outside candidate universe: ' + cid)
        if not c.get('evidence') or not c.get('deduplication'):
            errors.append('Missing evidence/deduplication: ' + cid)
        action = c.get('actionable_set')
        if action not in [None, 'A', 'B']:
            errors.append('Unknown actionable set: ' + cid)
        if (status == 'MISSING_HIGH_CONFIDENCE') != (action == 'A'):
            errors.append('Set A/status mismatch: ' + cid)
        if status == 'MISSING_NEEDS_SCOPE_REVIEW' and action != 'B':
            errors.append('Scope review missing from Set B: ' + cid)
        if action == 'B' and (not c.get('decision_required') or status not in ['MISSING_NEEDS_SCOPE_REVIEW', 'AMBIGUOUS']):
            errors.append('Missing/invalid maintainer decision: ' + cid)
        if action:
            if not c.get('manual_review'):
                errors.append('Audit proposal must remain reviewable: ' + cid)
            for field in ['title', 'authors', 'year', 'venue', 'official_url', 'scope_reason', 'candidate_tasks', 'candidate_research_types']:
                if not c.get(field):
                    errors.append('Missing actionable field: ' + cid + ' ' + field)
            primary = [e for e in c.get('evidence', []) if e.get('kind') in ['primary', 'author_primary'] and e.get('url', '').startswith('https://') and e.get('capture_paths')]
            if not primary:
                errors.append('No captured primary evidence: ' + cid)
        if action == 'A' and any(c.get('deduplication', {}).get('exact_public', {}).values()):
            errors.append('Proposed addition matches public corpus: ' + cid)
        if status == 'EXISTING_METADATA_UPDATE' and not all(c.get(k) for k in ['existing_paper_id', 'current_metadata', 'proposed_metadata', 'metadata_changes']):
            errors.append('Incomplete metadata delta: ' + cid)
    expected = {s: sum(c.get('status') == s for c in works) for s in STATUSES[:-1]}
    actual = payload.get('counting', {}).get('status_counts', {})
    if any(actual.get(s, 0) != n for s, n in expected.items()) or sum(actual.values()) != len(works):
        errors.append('Status count reconciliation failed')
    if payload.get('counting', {}).get('unique_works_adjudicated') != len(works):
        errors.append('Unique work count reconciliation failed')
    if payload.get('counting', {}).get('frozen_encounters_count') != len(payload.get('frozen_encounters', [])):
        errors.append('Frozen count reconciliation failed')
    if 'actionable_sets' in payload:
        expected_sets = {s: sorted(c['candidate_id'] for c in works if c.get('actionable_set') == s) for s in ['A', 'B']}
        if set(payload['actionable_sets']) != {'A', 'B'} or any(sorted(payload['actionable_sets'].get(s, [])) != ids for s, ids in expected_sets.items()):
            errors.append('Actionable set reconciliation failed')
    for count_field, record_field in [('set_a_task_memberships', 'candidate_tasks'), ('set_a_research_type_memberships', 'candidate_research_types')]:
        reported = payload.get('counting', {}).get(count_field)
        calculated = dict(Counter(label for c in works if c.get('actionable_set') == 'A' for label in c.get(record_field, [])))
        if reported is not None and reported != calculated:
            errors.append('Membership count reconciliation failed: ' + count_field)
    return errors


def validate():
    baseline = read_json(OUT / 'baseline.json')
    changed = [p for p, expected in baseline['protected_sha256'].items() if not (ROOT / p).is_file() or hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != expected]
    saved = read_json(OUT / 'saved_105_checksums.json')
    saved_changed = [p for p, h in saved.items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h]
    ps = corpus()
    counts = {'papers': len(ps), 'relationships': len(read_json(ROOT / 'web/data/public_preview_map_data.json')['records']), 'formally_published': sum(p['publication_type'] != 'preprint' for p in ps), 'mapped': sum(p['has_map_location'] for p in ps)}
    errors = []
    # Preserve the interrupted baseline. Account only for independently committed,
    # non-corpus UI/test changes documented at resumption, never data exceptions.
    external_path = OUT / 'external_changes.json'
    accounted = []
    if external_path.exists():
        for item in read_json(external_path)['baseline_file_differences']:
            path = item['path']
            allowed = path in ['web/index.html', 'web/style.css'] or path.startswith('tests/')
            if allowed and path in changed and hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == item['current_sha256']:
                accounted.append(path)
    unexplained = sorted(set(changed) - set(accounted))
    if counts != {'papers': 623, 'relationships': 1392, 'formally_published': 514, 'mapped': 602}:
        errors.append('Corpus counts changed')
    candidates_path = OUT / 'candidates.json'
    if candidates_path.exists():
        payload = read_json(candidates_path)
        candidates = payload['works']
        errors.extend(candidate_errors(payload))
        for c in candidates:
            for e in c.get('evidence', []):
                for path in e.get('capture_paths', []):
                    if not (ROOT / path).is_file():
                        errors.append('Missing evidence capture: ' + path)
        discovery = read_json(OUT / 'discovery_records.json')
        screening = read_json(OUT / 'icml2026_screening.json')
        if payload['counting']['raw_discovery_records_inspected'] != len(discovery) + len(screening['selected']):
            errors.append('Discovery count reconciliation failed')
        reconciliation = dict(Counter(c['status'] for c in candidates))
    else:
        reconciliation = {}
        errors.append('Candidate file missing')
    manifest_path = OUT / 'source_manifest.json'
    for item in read_json(manifest_path) if manifest_path.exists() else []:
        if item.get('raw_path') and hashlib.sha256(gzip.decompress((ROOT / item['raw_path']).read_bytes())).hexdigest() != item['response_sha256']:
            errors.append('Source checksum mismatch: ' + item['raw_path'])
    result = {'counts': counts, 'baseline_files_checked': len(baseline['protected_sha256']), 'changed_baseline_files': changed, 'accounted_external_non_corpus_changes': accounted, 'unexplained_baseline_changes': unexplained, 'saved_checksums_checked': len(saved), 'changed_saved_checksums': saved_changed, 'candidate_counts': reconciliation, 'errors': errors}
    print(json.dumps(result, indent=2))
    return 1 if unexplained or saved_changed or errors else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    f = sub.add_parser('fetch')
    f.add_argument('url')
    f.add_argument('--label', default='primary evidence')
    c = sub.add_parser('compare')
    c.add_argument('title')
    sub.add_parser('validate')
    args = parser.parse_args()
    if args.command == 'fetch':
        print(json.dumps(fetch(args.url, args.label), indent=2))
    elif args.command == 'compare':
        print(json.dumps(compare({'title': args.title}), indent=2))
    else:
        raise SystemExit(validate())


if __name__ == '__main__':
    main()
