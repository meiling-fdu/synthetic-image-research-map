#!/usr/bin/env python3
"""Normalize only the recorded Tier 1 additions; preserve every baseline byte."""
import csv
import io
import json
from prepare_systematic_tier1 import ROOT, OUT
from paper_taxonomy import IMAGE_SCOPE_ORDER
from title_normalization import canonical_paper_title
from finalize_systematic_tier1 import STAMP


def main():
    path = OUT / 'planned_additions.json'
    additions = json.loads(path.read_text())
    # Refuse to replace a suffix that has changed since this task recorded it.
    # This repair is scoped to the original Tier 1 rows, not future curation.
    for name, rows in additions.items():
        base = OUT / 'baseline/data/curated' / name
        target = ROOT / 'data/curated' / name
        fields = next(csv.reader(base.open()))
        stream = io.StringIO(newline='')
        csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore').writerows(rows)
        assert target.read_bytes() == base.read_bytes() + stream.getvalue().encode(), name
    for name in ('papers.csv', 'paper_taxonomy.csv'):
        for row in additions[name]:
            row['image_scopes'] = ';'.join(x for x in IMAGE_SCOPE_ORDER if x in row['image_scopes'].split(';'))
    additions['institution_locations.csv'] = []
    fuse = next(p for p in additions['papers.csv'] if p['title'].startswith('FUSE:'))
    inst = next(i for i in additions['institutions.csv'] if i['canonical_name'] == 'Southeast University (Bangladesh)')
    additions['institution_location_review.csv'] = [dict(institution=inst['canonical_name'], canonical_institution_name=inst['canonical_name'], institution_id=inst['institution_id'], related_paper_id=fuse['paper_id'], title=fuse['title'], year=fuse['year'], doi=fuse['doi'], institution_authors='Farhad Uz Zaman', raw_affiliation='Department of Computer Science and Engineering, Southeast University, Dhaka, Bangladesh', evidence_source='Official university address; primary paper author block', evidence_url='https://seu.edu.bd/revised-notice-university-closed-from-1012-february-2026-due-to-13th-parliamentary-election', suggested_city='Dhaka', suggested_country='Bangladesh', matched_institution=inst['canonical_name'], suggested_canonical_institution=inst['canonical_name'], match_method='primary_source', confidence='high', review_status='pending_review', location_status='needs_coordinate_review', coordinate_status='missing', created_at=STAMP, updated_at=STAMP)]
    additions['venue_aliases.csv'] = [dict(alias='International Conference on Computer and Information Technology', venue_id=fuse['venue_id'], venue_name=fuse['venue_name'], venue_acronym='ICCIT', venue_type='conference', venue_track='main', review_status='confirmed', notes='FUSE final DOI 10.1109/ICCIT68739.2025.11491327; ICCIT 2025 header in accepted primary PDF.')]
    for rows in additions.values():
        for row in rows:
            if row.get('title'):
                row['title'] = canonical_paper_title(row['title'])
    for name, rows in additions.items():
        base = OUT / 'baseline/data/curated' / name
        target = ROOT / 'data/curated' / name
        # This task owns only the suffix. Assert the pre-task prefix before touching it.
        assert target.read_bytes().startswith(base.read_bytes()), name
        stream = io.StringIO(newline='')
        writer = csv.DictWriter(stream, fieldnames=next(csv.reader(base.open())), extrasaction='ignore')
        writer.writerows(rows)
        target.write_bytes(base.read_bytes() + stream.getvalue().encode())
    path.write_text(json.dumps(additions, indent=2, ensure_ascii=False) + '\n')
    receipt_path = OUT / 'insertion.json'
    receipt = json.loads(receipt_path.read_text())
    receipt['added'] = {n: len(r) for n, r in additions.items()}
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
