#!/usr/bin/env python3
"""Compare every pre-task public paper and exact author-specific affiliation."""
import json
from collections import Counter
from prepare_systematic_tier1 import ROOT, OUT
from paper_exclusions import records_share_any_identity


def main():
    old = json.loads((OUT / 'baseline/web/data/public_preview_papers.json').read_text())['records']
    new = json.loads((ROOT / 'web/data/public_preview_papers.json').read_text())['records']
    differences = []
    for p in old:
        found = [n for n in new if records_share_any_identity(p, n)]
        assert len(found) == 1, p['title']
        changed = sorted(k for k in set(p) | set(found[0]) if p.get(k) != found[0].get(k))
        if changed:
            differences.append({'title': p['title'], 'fields': changed})
    proposals = json.loads((OUT / 'proposals.json').read_text())['papers']
    for p in proposals:
        found, = [n for n in new if records_share_any_identity(p, n)]
        exported = {a['institution_id']: set(a['authors']) for a in found['author_institution_affiliations']}
        expected = {a['institution_id']: set(a['authors']) for a in p['affiliations'] if a['institution_id']}
        assert exported == expected, (p['title'], exported, expected)
    result = {'pre_existing_public_papers_checked': len(old), 'pre_existing_public_changes': differences,
              'new_paper_affiliation_groups_exact': len(proposals)}
    (OUT / 'existing_public_diff.json').write_text(json.dumps(result, indent=2) + '\n')
    assert not differences, differences
    print(json.dumps(result))


if __name__ == '__main__':
    main()
