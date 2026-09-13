#!/usr/bin/env python3
"""Compare the reconciled corpus to the task snapshot without mutating sources."""
import argparse
import hashlib
import json
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

try:
    from . import audit_key_paper_coverage as audit
    from .paper_exclusions import active_exclusions, matching_exclusion_rows
    from .key_paper_reconciliation import apply_decisions
    from .venues import resolve_venue
except ImportError:
    import audit_key_paper_coverage as audit
    from paper_exclusions import active_exclusions, matching_exclusion_rows
    from key_paper_reconciliation import apply_decisions
    from venues import resolve_venue

ROOT = audit.ROOT
OUTPUT = ROOT / 'docs/key_paper_reconciliation_integrity.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def field_changes(before, after):
    return {k: {'before': before.get(k), 'after': after.get(k)}
            for k in before.keys() | after.keys() if before.get(k) != after.get(k)}


def verify(baseline):
    decisions = audit.load_json_records(ROOT / audit.RECONCILIATION_PATH)
    assert len(decisions) == 46
    additions = [d for d in decisions if d['action'] == 'added_needs_review']
    papers = audit.load_csv(ROOT / 'data/curated/papers.csv')
    old = audit.load_csv(baseline / 'data/curated/papers.csv')
    current = {p['paper_id']: p for p in papers}
    assert len(current) == len(papers)
    changed = []
    for p in old:
        assert p['paper_id'] in current, 'Pre-existing paper removed'
        changes = field_changes(p, current[p['paper_id']])
        if changes:
            assert p['paper_id'] == 'curated:5fde2c559e029508e0c3' and set(changes) == {'title'}
            assert current[p['paper_id']]['title'] == p['title'].replace('\\n', ' ').replace('  ', ' ')
            changed.append({'paper_id': p['paper_id'], 'changes': changes})
    new_ids = set(current) - {p['paper_id'] for p in old}
    assert new_ids == {d['matched_record']['paper_id'] for d in additions}
    assert all(d['classification'] == 'MISSING_ADD' for d in additions)
    taxonomy = audit.load_csv(ROOT / 'data/curated/paper_taxonomy.csv')
    for path in ('data/curated/paper_taxonomy.csv', 'data/curated/paper_exclusions.csv', 'data/curated/venue_aliases.csv'):
        assert (ROOT / path).read_bytes().startswith((baseline / path).read_bytes()), f'Existing rows changed: {path}'
    mappings = audit.load_csv(ROOT / 'data/curated/author_institution_mappings.csv')
    for paper_id in new_ids:
        p = current[paper_id]
        assert p['curation_status'] == 'needs_review' and p['review_status'] == 'pending'
        rows = [r for r in taxonomy if r['paper_id'] == paper_id]
        assert len(rows) == 1 and rows[0]['taxonomy_status'] == 'needs_review'
        assert all(rows[0][k + '_status'] == 'needs_review' for k in ('tasks', 'image_scopes', 'research_types'))
        assert not any(m['paper_id'] == paper_id for m in mappings)
    # All other curated/manual source files must be byte-identical to the snapshot.
    allowed = {'data/curated/papers.csv', 'data/curated/paper_taxonomy.csv',
               'data/curated/paper_exclusions.csv', 'data/curated/venue_aliases.csv',
               'data/manual/key_paper_coverage_report.csv', 'data/manual/missing_author_mappings_report.csv'}
    unchanged = {}
    for folder in ('data/curated', 'data/manual'):
        for path in sorted((baseline / folder).rglob('*')):
            if not path.is_file():
                continue
            relative = str(path.relative_to(baseline))
            if relative not in allowed:
                assert (ROOT / relative).read_bytes() == path.read_bytes(), f'Unintended source change: {relative}'
                unchanged[relative] = sha(path)
    public = audit.load_json_records(ROOT / audit.PREVIEW_PAPERS_JSON)
    markers = audit.load_json_records(ROOT / audit.PREVIEW_JSON)
    public_changes = []
    for path, rows in ((audit.PREVIEW_PAPERS_JSON, public), (audit.PREVIEW_JSON, markers)):
        key = lambda p: p.get('id') or p.get('paper_id') or p.get('doi') or p['title']
        lookup = {key(p): p for p in rows}
        for p in audit.load_json_records(baseline / path):
            assert key(p) in lookup
            changes = field_changes(p, lookup[key(p)])
            if changes:
                assert p.get('paper_id') == 'curated:5fde2c559e029508e0c3' and set(changes) == {'title'}
                public_changes.append({'file': str(path), 'record': key(p), 'changes': changes})
    assert len(public) == 613 + len(new_ids) and len(markers) == 1425
    checks = []
    for d in additions:
        p = current[d['matched_record']['paper_id']]
        assert sum(r.get('paper_id') == p['paper_id'] for r in public) == 1
        others = [r for r in public + papers if r.get('paper_id') != p['paper_id']]
        values = audit.identity_values(p)
        collisions = {k: sorted({r['title'] for r in others if values[k] & audit.identity_values(r)[k]}) for k in values}
        collisions['normalized_exact_title'] = sorted({r['title'] for r in others if audit.norm_title(r['title']) == audit.norm_title(p['title'])})
        assert not any(collisions.values()), (p['title'], collisions)
        aliases = [d['checklist']['title'], p['title']]
        method = d['deduplication']['method_acronym'].split(': no title collision')[0]
        exact_aliases = sorted({r['title'] for r in others if any(audit.norm_title(a) == audit.norm_title(r['title']) for a in aliases)})
        method_hits = sorted({r['title'] for r in others if method.casefold() in r['title'].casefold()})
        assert not exact_aliases and not method_hits
        nearest = sorted({r['title'] for r in others}, key=lambda t: SequenceMatcher(None, audit.norm_title(t), audit.norm_title(p['title'])).ratio(), reverse=True)[:5]
        checks.append({'paper_id': p['paper_id'], 'title': p['title'], 'identifiers': values_to_lists(values),
                       'exact_collisions': collisions, 'original_title_collisions': exact_aliases,
                       'method': method, 'method_title_collisions': method_hits,
                       'bounded_fuzzy_candidates': nearest, 'evidence_decision': d['deduplication']['decision']})
    exclusions = audit.load_csv(ROOT / audit.EXCLUSIONS_PATH)
    prior_exclusions = audit.load_csv(baseline / audit.EXCLUSIONS_PATH)
    effective = apply_decisions(audit.load_csv(ROOT / audit.KEY_PATH), decisions)
    recognized = []
    for number, key in enumerate(effective, 1):
        matches = matching_exclusion_rows(key, active_exclusions(exclusions))
        if matches:
            assert len(matches) == 1
            recognized.append({'checklist_row': number, 'title': key['title'], 'exclusion_id': matches[0]['exclusion_id'],
                               'identity': {k: key.get(k, '') for k in ('doi', 'arxiv_id', 'openalex_url', 'year')},
                               'new_registry_row': matches[0] not in prior_exclusions})
    artifacts, totals, errors = audit.expected_artifacts()
    assert not errors and not audit.validate_artifacts()
    rows = audit.load_csv(ROOT / audit.OUT_PATH)
    counts = Counter(r['coverage_status'] for r in rows)
    assert sum(counts.values()) == totals['key_papers'] == 299
    assert all(totals[k] == counts[k] for k in audit.ALLOWED_STATUSES)
    assert totals['bibliography_covered'] == counts['covered_as_map_marker'] + counts['covered_in_public_preview_paper_list']
    for path, expected in artifacts.items():
        assert (ROOT / path).read_bytes() == expected.encode()
    cvww = resolve_venue('Computer Vision Winter Workshop', publication_type='conference')
    assert cvww.ambiguity_status == 'resolved'
    return {'baseline': str(baseline), 'baseline_public_papers': 613, 'final_audit': totals,
            'baseline_source_sha256': {p: sha(baseline / p) for p in sorted(allowed)},
            'final_source_sha256': {p: sha(ROOT / p) for p in sorted(allowed | {
                str(audit.PREVIEW_JSON), str(audit.PREVIEW_PAPERS_JSON), str(audit.RECONCILIATION_PATH)})},
            'published_only': sum(p['publication_type'] in {'conference', 'journal', 'book'} for p in public),
            'pre_existing_paper_changes': changed, 'pre_existing_public_record_changes': public_changes,
            'additions': [current[k] for k in sorted(new_ids)], 'deduplication': checks,
            'pre_existing_taxonomy_bytes_unchanged': True, 'unchanged_source_sha256': unchanged,
            'appended_exclusions': exclusions[len(prior_exclusions):], 'recognized_exclusions': recognized,
            'active_exclusions_before': len(active_exclusions(prior_exclusions)), 'active_exclusions_after': len(active_exclusions(exclusions)),
            'cvww_venue_id': cvww.venue_id, 'audit_fresh': True}


def values_to_lists(values):
    return {k: sorted(v) for k, v in values.items()}


def verify_current_curation():
    """Verify today's membership using the persisted pre-curation snapshot."""
    try:
        from .report_primary_paper_curation import build_audit, BASELINE
    except ImportError:
        from report_primary_paper_curation import build_audit, BASELINE
    primary = build_audit()
    artifacts, totals, errors = audit.expected_artifacts()
    assert not errors and not audit.validate_artifacts()
    rows = audit.load_csv(ROOT / audit.OUT_PATH)
    counts = Counter(r['coverage_status'] for r in rows)
    assert sum(counts.values()) == totals['key_papers'] == 299
    assert all(totals[k] == counts[k] for k in audit.ALLOWED_STATUSES)
    assert totals['public_papers'] == 620 and totals['excluded'] == 10
    assert totals['candidate_only'] == totals['missing_from_candidate_pool'] == 0
    decisions = audit.load_json_records(ROOT / audit.RECONCILIATION_PATH)
    additions = [d['matched_record']['paper_id'] for d in decisions if d['action'] == 'added_needs_review']
    assert len(additions) == 10 and set(additions) == {p['paper_id'] for p in primary['papers']}
    excluded = [p for p in primary['papers'] if p['public_status'] == 'excluded']
    assert len(excluded) == 3
    return {
        'baseline': str(BASELINE), 'baseline_public_papers': 623,
        'final_audit': totals, 'published_only': primary['summary']['published_only'],
        'integrity': primary['integrity'], 'additions': primary['papers'],
        'exclusion_identity_traces': excluded,
        'source_sha256': {str(p): sha(ROOT / p) for p in (*audit.INPUT_PATHS, BASELINE)},
        'audit_fresh': True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path,
                        help='Optional original reconciliation snapshot for historical verification; omit for current primary curation.')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = verify(args.baseline) if args.baseline else verify_current_curation()
    expected = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.check:
        return int(not OUTPUT.exists() or OUTPUT.read_text() != expected)
    OUTPUT.write_text(expected)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
