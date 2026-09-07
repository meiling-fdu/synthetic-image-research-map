#!/usr/bin/env python3
"""Read-only verification of the 2026-09-06 institution decisions and provenance.

Run from any directory. Prints the live Admin counters; never modifies curation.
The historical before/after snapshots are intentionally separate from live totals.
"""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.admin_review_queues import ReviewContext
from scripts.curated_locations import location_review_payload, queue_row_id


def verify():
    docs = ROOT / 'docs'
    before = json.loads((docs / 'pending_institution_resolution_before_2026-09-06.json').read_text())
    decisions = json.loads((docs / 'pending_institution_decisions_2026-09-06.json').read_text())
    original_ids = {row['institution_id'] for row in before['pending_rows']}
    assert len(decisions) == len(original_ids) == 29
    assert {row['institution_id'] for row in decisions} == original_ids
    def read(name):
        with (ROOT / 'data/curated' / name).open() as handle:
            return list(csv.DictReader(handle))
    institutions = {r['institution_id']: r for r in read('institutions.csv')}
    locations = {r['location_id']: r for r in read('institution_locations.csv')}
    reviews = {queue_row_id(r): r for r in read('institution_location_review.csv')}
    aliases = read('institution_aliases.csv')
    mappings = read('author_institution_mappings.csv')
    context = ReviewContext()
    payload = location_review_payload(mappings=context.rows['mappings'], exclusions=context.rows['exclusions'], paper_is_suppressed=context.paper_suppression)
    effective_reviews = {row['queue_id']: row for row in payload['records']}
    for decision in decisions:
        source, target = decision['institution_id'], decision['target_id']
        if decision['raw_file']:
            assert hashlib.sha256((ROOT / decision['raw_file']).read_bytes()).hexdigest() == decision['raw_sha256']
        assert decision['evidence_urls'] and decision['reason'] and decision['provider_decision']
        if decision['decision'] == 'REMAIN PENDING':
            assert not decision['location_id']
        else:
            location = locations[decision['location_id']]
            assert location['institution_id'] == target
            for field in ('city', 'region', 'country', 'country_code', 'lat', 'lon'):
                assert str(location[field]) == str(decision[field]), (source, field)
        if decision['decision'] == 'ALIAS':
            assert institutions[source]['institution_status'] == 'merged'
            assert institutions[target]['institution_status'] == 'active'
            assert any(r['institution_id'] == target and r['alias_name'] == decision['original_name'] for r in aliases)
            assert not any(r['institution_id'] == source for r in mappings)
        for original in before['pending_rows']:
            if original['institution_id'] != source or not original['review_row_persisted']:
                continue
            review = reviews[original['queue_id']]
            assert review['related_paper_id'] == original['related_paper_id']
            assert review['institution_id'] == target
            expected = {'CONFIRM':'confirmed', 'ALIAS':'alias_of_confirmed', 'REMAIN PENDING':'pending_review'}[decision['decision']]
            assert effective_reviews[original['queue_id']]['review_status'] == expected, source
    context = ReviewContext()
    payload = location_review_payload(mappings=context.rows['mappings'], exclusions=context.rows['exclusions'], paper_is_suppressed=context.paper_suppression)
    return payload['summary']


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
