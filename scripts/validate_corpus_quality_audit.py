#!/usr/bin/env python3
"""Read-only validator for the 2026-10-04 corpus quality audit.

Run from any directory. This checks review-queue integrity, not whether a
scientific recommendation should be accepted. It never writes corpus data.
"""
from __future__ import annotations

import collections
import csv
import hashlib
import json
from pathlib import Path

try:
    from .curated_export import PaperIdentityCache, PaperIdentityIndex
except ImportError:
    from curated_export import PaperIdentityCache, PaperIdentityIndex

ROOT = Path(__file__).resolve().parents[1]
AUDIT = Path('data/raw/corpus_quality_audit_2026_10_04')
QUEUE_NAMES = ('unmapped_papers', 'taxonomy_review', 'relationship_review',
               'publication_metadata_review')
TAXONOMY_STATUSES = {'HIGH_CONFIDENCE_FIX': 'A', 'LIKELY_FIX': 'B',
                     'MAINTAINER_REVIEW': 'C', 'NO_CHANGE_AFTER_REVIEW': 'D'}
LABELS = {'tasks': {'detection', 'source_attribution', 'localization'},
          'research_types': {'method', 'dataset', 'benchmark', 'survey', 'analysis_study'}}
UNMAPPED_STATUSES = {'AUTO_FIX_CANDIDATE': 'A', 'EVIDENCE_CAN_RESOLVE': 'B',
                     'MAINTAINER_REVIEW': 'C', 'LEGITIMATELY_UNMAPPED': 'D'}
BLOCKERS = {'NO_AFFILIATION_EVIDENCE', 'AFFILIATION_UNRESOLVED',
            'INSTITUTION_UNRESOLVED', 'INSTITUTION_LOCATION_UNRESOLVED',
            'PUBLICATION_SOURCE_INACCESSIBLE', 'INTENTIONALLY_UNMAPPED',
            'DATA_PIPELINE_INCONSISTENCY', 'OTHER_REVIEW_REQUIRED'}
FORMAL_STATUSES = {'COMPLETE_FOR_CURRENT_SCHEMA', 'MISSING_RECOVERABLE_METADATA',
                   'FIELD_NOT_SUPPORTED_BY_SCHEMA', 'SOURCE_CONFLICT', 'REVIEW_REQUIRED'}
NONFORMAL_STATUSES = {'TRUE_PREPRINT', 'WORKSHOP_NONARCHIVAL', 'CHALLENGE_REPORT',
                      'FORMAL_VERSION_FOUND', 'FORMAL_VERSION_POSSIBLE',
                      'PUBLICATION_STATUS_AMBIGUOUS', 'OTHER'}
RELATIONSHIP_ISSUES = {'DUPLICATE_PAPER_INSTITUTION_PAIR', 'AUTHOR_AFFILIATION_OVERASSIGNMENT',
                     'AUTHOR_STRING_MISMATCH', 'PUBLIC_INSTITUTION_NOT_IN_CURATED_REGISTRY',
                     'PARENT_CHILD_COAFFILIATION', 'RECOMPUTE_AFTER_AFFILIATION_REPAIR'}
EXPECTED = {'public': 640, 'formal': 529, 'mapped': 617, 'unmapped': 23,
            'relationship_rows': 1423, 'unique_paper_institution_pairs': 1422}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def csv_rows(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def load_context(root=ROOT):
    papers = read_json(root / 'web/data/public_preview_papers.json')['records']
    maps = read_json(root / 'web/data/public_preview_map_data.json')['records']
    taxonomy = csv_rows(root / 'data/curated/paper_taxonomy.csv')
    index = PaperIdentityIndex(taxonomy, PaperIdentityCache())
    by_id, taxonomy_by_id, taxonomy_to_id = {}, {}, {}
    for paper in papers:
        matches = index.matches(paper)
        if len(matches) != 1:
            raise ValueError(f'Expected one existing taxonomy identity: {paper["title"]}')
        entry = matches[0]
        pid = paper.get('paper_id') or entry['taxonomy_id']
        by_id[pid] = paper
        taxonomy_by_id[pid] = entry
        taxonomy_to_id[entry['taxonomy_id']] = pid
    pairs = collections.Counter()
    for row in maps:
        matches = index.matches(row)
        if len(matches) != 1:
            raise ValueError(f'Expected one relationship identity: {row["id"]}')
        pairs[taxonomy_to_id[matches[0]['taxonomy_id']], row['institution_id']] += 1
    institutions = {r['institution_id'] for r in csv_rows(root / 'data/curated/institutions.csv')}
    institutions.update(r['institution_id'] for r in maps)
    frozen_records = read_json(root / 'data/manual/neurips_2026_targeted_gap_fill_reconciliation.json')['records']
    frozen_ids = {r.get('existing_authoritative_paper_id') for r in frozen_records}
    frozen_arxiv = {r.get('arxiv_id') for r in frozen_records if r.get('arxiv_id')}
    frozen_ids.update(pid for pid, p in by_id.items() if p.get('arxiv_id') in frozen_arxiv)
    mapped = {pid for pid, _ in pairs}
    formal = {pid for pid, p in by_id.items() if p['publication_type'] != 'preprint'}
    return dict(papers=by_id, taxonomy=taxonomy_by_id, institutions=institutions,
                frozen=frozen_ids - {None}, formal=formal, pairs=pairs,
                unmapped=set(by_id) - mapped,
                counts=dict(public=len(by_id), formal=len(formal), mapped=len(mapped),
                            unmapped=len(by_id)-len(mapped), relationship_rows=len(maps),
                            unique_paper_institution_pairs=len(pairs)))


def load_queues(root=ROOT):
    return {name: read_json(root / AUDIT / (name + '.json')) for name in QUEUE_NAMES}


def decision_rows(queues):
    for name in QUEUE_NAMES[:3]:
        yield from queues[name]['records']
    pub = queues['publication_metadata_review']
    yield from pub['formal_records']
    yield from pub['nonformal_records']


def batch_counts(queues):
    return {key: sum(r['batch'] == key for r in decision_rows(queues)) for key in 'ABCD'}


def validate(queues, context):
    errors = []
    def check(condition, message):
        if not condition:
            errors.append(message)
    check(context['counts'] == EXPECTED, 'authoritative corpus counts changed')
    seen_ids = set()
    for row in decision_rows(queues):
        rid, pid = row.get('review_id'), row.get('paper_id')
        check(bool(rid) and rid not in seen_ids, f'duplicate/missing review ID: {rid}')
        seen_ids.add(rid)
        check(pid in context['papers'], f'invalid paper ID: {pid}')
        if pid in context['papers']:
            check(row.get('title') == context['papers'][pid]['title'], f'paper title/identity mismatch: {rid}')
        check(row.get('batch') in {'A', 'B', 'C', 'D'}, f'invalid batch: {rid}')
        check(row.get('batch') == 'D' or pid not in context['frozen'], f'frozen actionable identity: {rid}')
        check(bool(row.get('reason') or row.get('recommended_action')), f'missing decision reason: {rid}')
        if row.get('batch') in ['B', 'C']:
            check(bool(row.get('evidence_required') or row.get('recommended_action')), f'missing evidence/decision requirement: {rid}')
        ids = list(row.get('institution_ids', []))
        ids += [i.get('institution_id') for i in row.get('institutions', []) if i.get('institution_id')]
        for iid in ids:
            check(iid in context['institutions'], f'invalid institution ID: {iid}')

    unmapped = queues['unmapped_papers']
    records = unmapped['records']
    check(len(records) == 23 and {r['paper_id'] for r in records} == context['unmapped'], 'unmapped coverage must equal the 23 baseline identities')
    for r in records:
        check(r['primary_classification'] in BLOCKERS, f'invalid blocker: {r["review_id"]}')
        check(UNMAPPED_STATUSES.get(r['remediation_category']) == r['batch'], f'invalid unmapped status/batch: {r["review_id"]}')
    check(collections.Counter(r['remediation_category'] for r in records) == collections.Counter(unmapped['counts']), 'unmapped category counts do not reconcile')
    check(collections.Counter(r['primary_classification'] for r in records) == collections.Counter(unmapped['primary_classification_counts']), 'unmapped blocker counts do not reconcile')

    taxonomy = queues['taxonomy_review']
    check(taxonomy['coverage_count'] == 640 and len(taxonomy['coverage']) == 640 and {r['paper_id'] for r in taxonomy['coverage']} == set(context['papers']), 'taxonomy coverage must contain 640 existing identities')
    record_by_key = {}
    for r in taxonomy['records']:
        key = r['paper_id'], r['dimension']
        check(key not in record_by_key, f'duplicate taxonomy decision: {key}')
        record_by_key[key] = r
        allowed = LABELS.get(r['dimension'], set())
        check(r['dimension'] in LABELS, f'invalid taxonomy dimension: {r["review_id"]}')
        for field in ['current_labels', 'proposed_labels']:
            check(set(r[field]) <= allowed and len(set(r[field])) == len(r[field]), f'invalid labels: {r["review_id"]} {field}')
        expected = context['taxonomy'].get(r['paper_id'], {}).get(r['dimension'], '').split(';')
        check(r['current_labels'] == [v for v in expected if v], f'current labels differ from registry: {r["review_id"]}')
        check(TAXONOMY_STATUSES.get(r['status']) == r['batch'], f'invalid taxonomy status/batch: {r["review_id"]}')
        if r['status'] == 'NO_CHANGE_AFTER_REVIEW':
            check(r['current_labels'] == r['proposed_labels'], f'no-change label mutation: {r["review_id"]}')
        check(bool(r.get('evidence_url')) and bool(r.get('confidence')), f'missing taxonomy evidence/confidence: {r["review_id"]}')
        for dim in LABELS:
            current = [v for v in context['taxonomy'].get(r['paper_id'], {}).get(dim, '').split(';') if v]
            check(r.get('current_' + dim) == current, f'companion current labels mismatch: {r["review_id"]}')
            proposed = r['proposed_labels'] if r['dimension'] == dim else current
            check(r.get('proposed_' + dim) == proposed, f'companion proposed labels mismatch: {r["review_id"]}')
    for dim in LABELS:
        counts = collections.Counter(r['status'] for r in taxonomy['records'] if r['dimension'] == dim)
        check(sum(counts.values()) == 640 and counts == collections.Counter(taxonomy['counts'][dim]), f'taxonomy counts do not reconcile: {dim}')
        check(counts == collections.Counter(taxonomy['coverage_outcome_counts'][dim]), f'taxonomy outcome counts differ: {dim}')
    for c in taxonomy['coverage']:
        for dim in LABELS:
            r = record_by_key.get((c['paper_id'], dim), {})
            check(c['outcomes'][dim] == {'status': r.get('status'), 'review_id': r.get('review_id')}, f'taxonomy outcome mismatch: {c["paper_id"]} {dim}')

    pub = queues['publication_metadata_review']
    for group, expected_ids, allowed in [('formal', context['formal'], FORMAL_STATUSES), ('nonformal', set(context['papers'])-context['formal'], NONFORMAL_STATUSES)]:
        rows = pub[group + '_records']
        check(len(rows) == len(expected_ids) and {r['paper_id'] for r in rows} == expected_ids, f'{group} coverage mismatch')
        check(pub[group + '_count'] == len(rows), f'{group} declared count mismatch')
        check(collections.Counter(r['status'] for r in rows) == collections.Counter(pub[group + '_status_counts']), f'{group} status counts do not reconcile')
        for r in rows:
            check(r['status'] in allowed, f'invalid publication status: {r["review_id"]}')
            if r['status'] == 'FORMAL_VERSION_FOUND':
                v = r.get('formal_version', {})
                check(all(v.get(k) for k in ['venue','year','publication_type','canonical_url','identity_evidence','confidence']), f'incomplete formal-version identity evidence: {r["review_id"]}')
                check(r['batch'] == 'A' and r['current']['publication_type'] == 'preprint', f'invalid publication upgrade: {r["review_id"]}')
            if r['status'] == 'MISSING_RECOVERABLE_METADATA':
                check(bool(r.get('missing_fields')) and bool(r.get('authoritative_source')) and bool(r.get('proposed_changes')), f'incomplete recoverable metadata evidence: {r["review_id"]}')
            check(not ({'volume','issue','pages'} & set(r.get('proposed_changes',{}))), f'unsupported schema remediation: {r["review_id"]}')

    rel = queues['relationship_review']
    check(rel['counts']['relationship_rows'] == 1423 and rel['counts']['unique_paper_institution_pairs'] == 1422, 'relationship counts mismatch')
    check(rel['counts']['duplicate_pair_groups'] == sum(n > 1 for n in context['pairs'].values()), 'duplicate-pair count mismatch')
    seen = set()
    for r in rel['records']:
        key = r['paper_id'], r['issue'], tuple(sorted(r['institution_ids']))
        check(key not in seen, f'duplicate relationship review: {key}')
        seen.add(key)
        check(r['issue'] in RELATIONSHIP_ISSUES, f'invalid relationship issue: {r["review_id"]}')
        if r['issue'] == 'DUPLICATE_PAPER_INSTITUTION_PAIR':
            check(r.get('recommendation') in {'KEEP_AS_DISTINCT_PROVENANCE_ROWS','MERGE_RECOMMENDED','REQUIRES_MAINTAINER_DECISION'}, 'invalid UCSB recommendation')
            check(len(r.get('rows', [])) == 2, 'UCSB review must preserve both source rows')
    for group in rel['coordinate_observations']:
        check(set(group['institution_ids']) <= context['institutions'], 'invalid coordinate-observation institution')
    actions = {r.get('action_key'): r for r in rel['records'] if r.get('action_key')}
    check(set(actions) == {'R1', 'R2', 'R3'}, 'UCSB must preserve separate R1/R2/R3 proposals')
    if set(actions) == {'R1', 'R2', 'R3'}:
        check(actions['R2'].get('depends_on') == [actions['R1']['review_id']], 'R2 must depend on R1')
        check(actions['R3'].get('depends_on') == [actions['R2']['review_id']], 'R3 must depend on R2')
    return errors


def changed_paths(root, manifest):
    return [name for name, expected in manifest.items()
            if not (root/name).is_file() or hashlib.sha256((root/name).read_bytes()).hexdigest() != expected]


def main():
    try:
        from .corpus_quality_history import predecessor_root
        from .validate_corpus_quality_batch_a import validation_payload
    except ImportError:
        from corpus_quality_history import predecessor_root
        from validate_corpus_quality_batch_a import validation_payload
    queues = load_queues()
    with predecessor_root() as root:
        context = load_context(root)
    errors = validate(queues, context)
    baseline = read_json(ROOT / AUDIT / 'baseline.json')
    remediation = validation_payload()
    errors.extend(remediation['errors'])
    checks = {'UNEXPECTED_CHANGED': remediation['unexpected_changed'],
              'FROZEN_NEURIPS_CHANGED': changed_paths(ROOT, baseline['frozen_neurips_sha256']),
              'PREEXISTING_LOCAL_FILES_CHANGED': changed_paths(ROOT, baseline['preexisting_local_sha256'])}
    if len(baseline['preexisting_local_sha256']) != 128:
        errors.append('preexisting local inventory must contain 128 files')
    for name, changed in checks.items():
        print(f'{name} = {len(changed)}')
        errors.extend(f'{name}: {p}' for p in changed)
    print(json.dumps({'corpus':context['counts'], 'batches':batch_counts(queues),
                      'review_decisions':sum(batch_counts(queues).values()), 'errors':errors}, indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
