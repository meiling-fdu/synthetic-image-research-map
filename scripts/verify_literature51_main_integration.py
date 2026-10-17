#!/usr/bin/env python3
"""Verify the reviewed literature delta against the published remote baseline.

The original import/follow-up receipts remain immutable historical checkpoints.
This successor verifies exact remote CSV prefixes/rows plus their reviewed delta,
all remote public objects and the complete map, without retrieval or imports.
"""
from collections import Counter
from copy import deepcopy
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path('data/processed/literature51_2026_10_16/main_integration/manifest.json')


def baseline_bytes(root, relative):
    manifest = json.loads((root / MANIFEST).read_text())
    return subprocess.check_output(['git', 'show', manifest['remote_base'] + ':' + relative], cwd=root)


def csv_rows(content):
    return list(csv.DictReader(io.StringIO(content.decode('utf-8-sig'), newline='')))


def expected_csv(root, name):
    from scripts.migrate_systematic_gap_2026_10_03 import csv_delta_bytes
    folder = root / 'data/processed/literature51_2026_10_16'
    plan = json.loads((folder / 'plan.json').read_text())
    followup = json.loads((folder / 'followup/receipt.json').read_text())
    original = baseline_bytes(root, 'data/curated/' + name)
    additions = deepcopy(plan['additions'][name])
    # E17 is a new row in this delta. Patch it before appending so none of the
    # published taxonomy rows or their mixed line endings are reserialized.
    for patch in followup.get('patches', {}).get(name, []):
        matches = [row for row in additions if row['paper_id'] == patch['paper_id']]
        assert len(matches) == 1, 'A follow-up patch must target a new literature row'
        row = matches[0]
        assert all(row[key] == value for key, value in patch['before'].items())
        row.update(patch['after'])
    additions += followup.get('additions', {}).get(name, [])
    return csv_delta_bytes(original, additions, [])


def verify_inventory(root):
    manifest = json.loads((root / MANIFEST).read_text())
    entries = subprocess.check_output(['git', 'ls-tree', '-r', '-z', manifest['remote_base']], cwd=root).split(b'\0')
    blobs = {entry.split(b'\t', 1)[1].decode(): entry.split(b'\t', 1)[0].split()[-1].decode() for entry in entries if entry}
    remote = set(blobs)
    tracked = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')) - {''}
    assert tracked == remote | set(manifest['changed_paths']), 'Unexpected checkout inventory'
    for relative in remote - set(manifest['changed_paths']):
        content = (root / relative).read_bytes()
        assert hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest() == blobs[relative], relative
    for relative, digest in manifest['preserved_literature_sha256'].items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest, relative
    return manifest


def check(root=ROOT):
    from scripts import integrate_literature51_2026_10_16 as batch
    from scripts import reassess_literature51_2026_10_16 as followup
    from scripts.literature51_reproducibility import materialize_export_inputs, verify_workspace_files
    manifest = verify_inventory(root)
    restored = materialize_export_inputs(root)
    baseline = batch.read(root / batch.OUT / 'baseline.json')
    scope = verify_workspace_files(root, baseline['untracked_sha256'])
    preflight = batch.read(root / batch.OUT / 'followup/commit_preflight.json')
    remote_paths = set(subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', manifest['remote_base']], cwd=root).decode().splitlines())
    assert all(not (root / p).exists() for p in set(preflight['excluded_local_paths']) - remote_paths)
    untracked = set(subprocess.check_output(['git', 'ls-files', '-o', '--exclude-standard', '-z'], cwd=root).decode().split('\0')) - {''}
    assert untracked <= set(restored), 'Unexpected untracked dependency'
    plan = batch.read(root / batch.OUT / 'plan.json')
    event = followup.receipt(root)
    review = batch.read(root / followup.OUT / 'review.json')
    imported = {a['candidate_id']: a['paper_id'] for a in plan['audit'] if a['decision'] == 'import'}
    imported['B03'] = event['paper_id']
    held = set(review['held'])
    assert len(imported) == 39 and len(held) == 12
    assert not set(imported) & held
    assert set(imported) | held == set(batch.EXPECTED)
    for name in plan['additions']:
        assert (root / 'data/curated' / name).read_bytes() == expected_csv(root, name), name
        assert (root / 'data/curated' / name).read_bytes().startswith(baseline_bytes(root, 'data/curated/' + name)), name
        key = {'review_decisions.csv': 'decision_id', 'paper_taxonomy.csv': 'taxonomy_id'}.get(name, 'paper_id')
        if name != 'venue_aliases.csv':
            current = {r[key]: r for r in batch.rows(root / 'data/curated' / name)}
            for old in csv_rows(baseline_bytes(root, 'data/curated/' + name)):
                assert current[old[key]] == old, (name, old[key])
    papers = batch.read(root / 'web/data/public_preview_papers.json')['records']
    curated_papers = batch.rows(root / 'data/curated/papers.csv')
    maps = batch.read(root / 'web/data/public_preview_map_data.json')['records']
    remote_papers = json.loads(baseline_bytes(root, 'web/data/public_preview_papers.json'))['records']
    remote_maps = json.loads(baseline_bytes(root, 'web/data/public_preview_map_data.json'))['records']
    assert maps == remote_maps, 'Remote map objects or order changed'
    current = {batch.title_key(p['title']): p for p in papers}
    for old in remote_papers:
        assert current[batch.title_key(old['title'])] == old, old['title']
    assert {p['paper_id'] for p in papers if batch.title_key(p['title']) not in {batch.title_key(o['title']) for o in remote_papers}} == set(imported.values())
    for a in plan['audit']:
        for name, collection in [('public', papers), ('curated', curated_papers)]:
            matches = batch.identity_matches(a, {name: collection})
            assert len(matches) == (0 if a['candidate_id'] in held else 1), (a['candidate_id'], name)
    for collection in (papers, curated_papers):
        for field, normalize in [('title', batch.title_key), ('doi', batch.normalize_doi), ('arxiv_id', batch.normalize_arxiv_id)]:
            values = Counter(normalize(p.get(field)) for p in collection if normalize(p.get(field)))
            assert all(n == 1 for n in values.values()), field
    assert len({p.get('paper_id') for p in papers if p.get('paper_id')}) == sum(bool(p.get('paper_id')) for p in papers)
    for source in batch.read(root / batch.RAW / 'source_manifest.json'):
        if source.get('raw_path') and (root / source['raw_path']).exists():
            batch.source_body(root, source)
    batch.extract_metadata(root)  # Compact primary evidence is sufficient offline.
    counts = {
        'curated': len(batch.rows(root / 'data/curated/papers.csv')),
        'public': len(papers), 'formal': sum(p['publication_type'] in ('journal', 'conference', 'book') for p in papers),
        'mapped': sum(bool(p['has_map_location']) for p in papers), 'unmapped': sum(not p['has_map_location'] for p in papers),
        'relationship_rows': len(maps), 'taxonomy_pending': sum(t['taxonomy_status'] == 'needs_review' for t in batch.rows(root / 'data/curated/paper_taxonomy.csv')),
        'review_decisions': len(batch.rows(root / 'data/curated/review_decisions.csv')),
    }
    assert counts == manifest['counts'], counts
    return {'candidate_count': 51, 'counts': {'import': 39, 'held': 12}, 'corpus': counts,
            'historical_and_unrelated_files_preserved': True, 'workspace_verification_scope': scope,
            'remote_public_objects_unchanged': len(remote_papers), 'remote_map_objects_unchanged': len(remote_maps),
            'unexplained': 0, 'restored_committed_inputs': restored}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
