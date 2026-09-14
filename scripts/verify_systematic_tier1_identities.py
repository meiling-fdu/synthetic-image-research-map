#!/usr/bin/env python3
"""Read-only final identifier/title/version audit of the integrated corpus."""
import json
from collections import defaultdict
from prepare_systematic_tier1 import ROOT, OUT
from audit_key_paper_coverage import norm_title
from paper_exclusions import all_identity_keys, records_share_any_identity
from reconcile_systematic_literature import read_csv


def main():
    papers = json.loads((ROOT / 'web/data/public_preview_papers.json').read_text())['records']
    curated = read_csv(ROOT / 'data/curated/papers.csv')
    groups = defaultdict(set)
    for index, paper in enumerate(papers):
        for key in all_identity_keys(paper):
            if key.startswith(('doi:', 'arxiv:', 'openalex:')):
                groups[key].add(index)
        groups['normalized_title:' + norm_title(paper['title'])].add(index)
    duplicates = {k: [papers[i]['title'] for i in sorted(v)] for k, v in groups.items() if len(v) > 1}
    assert not duplicates, duplicates
    detective = [p for p in papers if p['title'].startswith('Detective SAM:')]
    assert len(detective) == 1 and detective[0]['year'] == 2026
    forenx, = [p for p in curated if p['title'].startswith('ForenX:')]
    plada, = [p for p in curated if p['title'].startswith('Pay Less Attention to Deceptive Artifacts:')]
    assert not records_share_any_identity(forenx, plada)
    fuse, = [p for p in papers if p['title'].startswith('FUSE:')]
    collisions = [p for p in papers if p['title'].startswith(('FUSED:', 'Organic or Diffused:'))]
    assert len(collisions) == 2
    assert not any(records_share_any_identity(fuse, p) for p in collisions)
    result = {'public_papers': len(papers), 'duplicate_identifier_or_normalized_title_groups': duplicates,
              'detective_sam_canonical_records': len(detective), 'forenx_distinct_from_plada': True,
              'fuse_distinct_from_fused_and_diffused': True}
    (OUT / 'final_identity_audit.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
