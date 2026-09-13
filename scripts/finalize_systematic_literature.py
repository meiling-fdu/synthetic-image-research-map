#!/usr/bin/env python3
"""Create the new manual audit registry once, refusing to overwrite decisions."""
from report_systematic_literature import CANONICAL, read_csv, accounting, generate
from collect_systematic_literature import PROCESSED
from screen_systematic_literature import STATUSES


def finalize():
    draft = PROCESSED / 'candidate_registry_draft.csv'
    rows = read_csv(draft)
    assert len({r['candidate_id'] for r in rows}) == len(rows)
    assert all(r['final_status'] in STATUSES for r in rows)
    stats = accounting(rows)
    assert all(sum(s['reference_outcomes'].values()) == s['enumerated'] for s in stats['surveys'])
    # Exclusive creation is intentional: reruns may regenerate reports, not manual decisions.
    with CANONICAL.open('xb') as handle:
        handle.write(draft.read_bytes())
    generate()


if __name__ == '__main__':
    finalize()
