"""Exact B4-04 live-source protection, independent of historical test views."""
from functools import lru_cache
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = '2932b9a5b58a8c84761e381668925a765ca9719e'
FIXTURES = 'tests/fixtures/batch_b_b4_04'
MANIFEST_SHA256 = '82e6592d020b69bb85341ffe7a495d5beab2b0673e3f8757ff5f0c900ec14b89'
TREE_SHA256 = '66edd718661f78a66d802ab69d4c135b28798995a373cfb1cc47000d54d693b1'
TREE_GZIP_SHA256 = '363d7634085471ab5046ae89417d9d4af2278495441defb45feed3332c0796be'
PORTABLE_INDEX_SHA256 = '18076dcbb6240bb148a708a79141970198b1d1eaad428dfbdcf02cfcff667a5e'
NEW_CODE_PATHS = (
    'conftest.py', 'tests/b4_04_state.py', 'tests/b5_02_historical_fixtures.py',
    'tests/test_corpus_quality_batch_b_wave_b4_04.py', 'tests/test_b4_04_regression_boundaries.py',
)
SOURCE_PATHS = ('data/curated/papers.csv', 'data/curated/paper_taxonomy.csv', 'data/curated/review_decisions.csv')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def rows(raw):
    return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'), newline='')))


def authorize():
    assert (BASE, FIXTURES, MANIFEST_SHA256, TREE_SHA256, TREE_GZIP_SHA256, PORTABLE_INDEX_SHA256, NEW_CODE_PATHS, SOURCE_PATHS) == (
        '2932b9a5b58a8c84761e381668925a765ca9719e', 'tests/fixtures/batch_b_b4_04',
        '82e6592d020b69bb85341ffe7a495d5beab2b0673e3f8757ff5f0c900ec14b89',
        '66edd718661f78a66d802ab69d4c135b28798995a373cfb1cc47000d54d693b1',
        '363d7634085471ab5046ae89417d9d4af2278495441defb45feed3332c0796be',
        '18076dcbb6240bb148a708a79141970198b1d1eaad428dfbdcf02cfcff667a5e',
        ('conftest.py', 'tests/b4_04_state.py', 'tests/b5_02_historical_fixtures.py',
         'tests/test_corpus_quality_batch_b_wave_b4_04.py', 'tests/test_b4_04_regression_boundaries.py'),
        ('data/curated/papers.csv', 'data/curated/paper_taxonomy.csv', 'data/curated/review_decisions.csv'),
    ), 'Unreviewed B4-04 authorization metadata'


def manifest(root=ROOT):
    authorize()
    raw = (root / FIXTURES / 'adjudication_manifest.json').read_bytes()
    assert sha(raw) == MANIFEST_SHA256, 'Unreviewed B4-04 decision manifest'
    value = json.loads(raw)
    assert value['baseline_commit'] == BASE
    assert tuple(value['approved_data_files']) == SOURCE_PATHS
    return value


def published_tree(root=ROOT):
    authorize()
    compressed = (root / FIXTURES / 'published_tree_sha256.json.gz').read_bytes()
    assert sha(compressed) == TREE_GZIP_SHA256, 'Changed published-tree archive'
    raw = gzip.decompress(compressed)
    assert sha(raw) == TREE_SHA256, 'Unreviewed published-tree inventory'
    value = json.loads(raw)
    assert value['commit'] == BASE and len(value['files']) == 4832
    return value['files']


@lru_cache(maxsize=None)
def published_bytes(path, root=ROOT):
    authorize()
    return subprocess.check_output(['git', '--no-optional-locks', 'show', BASE + ':' + path], cwd=root)


def validate_source_bytes(blobs, root=ROOT):
    """Reject changes outside the independently accepted field/decision delta."""
    m = manifest(root)
    assert set(blobs) == set(SOURCE_PATHS), 'Unexpected authoritative source path'
    before = {p: published_bytes(p, root) for p in SOURCE_PATHS}
    assert {p: sha(b) for p, b in before.items()} == m['source_before_sha256']
    changes = []
    for path, key in [(SOURCE_PATHS[0], 'paper_id'), (SOURCE_PATHS[1], 'taxonomy_id')]:
        old, now = rows(before[path]), rows(blobs[path])
        assert [r[key] for r in old] == [r[key] for r in now], 'Changed paper/taxonomy identity or order'
        for a, b in zip(old, now):
            assert a.keys() == b.keys()
            changes.extend({'path': path, 'key_field': key, 'key': a[key], 'field': k,
                            'before': a[k], 'after': b[k]} for k in a if a[k] != b[k])
    sort = lambda values: sorted(values, key=lambda v: (v['path'], v['key'], v['field']))
    assert sort(changes) == sort(m['cell_deltas']), 'Unauthorized B4-04 semantic delta'
    current_decisions = rows(blobs[SOURCE_PATHS[2]])
    old_decisions = before[SOURCE_PATHS[2]]
    assert blobs[SOURCE_PATHS[2]].startswith(old_decisions), 'Changed original decision bytes'
    assert len(rows(old_decisions)) == 138
    assert len(current_decisions) == len({d['decision_id'] for d in current_decisions}) == 151
    assert current_decisions[138:] == [r['formal_decision'] for r in m['records']]
    assert len({r['action_fingerprint'] for r in m['records']}) == 13
    accepted = {r['review_id'] for r in m['records'] if r['accepted']}
    held = {r['review_id'] for r in m['records'] if not r['accepted']}
    assert accepted == {'R124', 'R149', 'R223', 'R363', 'R477', 'R509', 'R512', 'R625'}
    assert held == {'R045', 'R156', 'R251', 'R284', 'P251'}
    assert all(r['formal_decision']['action'] == ('no_action_after_review' if r['accepted'] else 'unresolved')
               for r in m['records'])
    assert {p: sha(b) for p, b in blobs.items()} == m['source_after_sha256'], 'Unreviewed source bytes'
    return {'formal_decisions': len(current_decisions), 'appended': 13, 'changed_cells': len(changes)}


def assert_current_state(root=ROOT, reader=None):
    """Historical success never exempts the real current files from protection."""
    read = reader or (lambda path: (root / path).read_bytes())
    assert subprocess.run(['git', '--no-optional-locks', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=root).returncode == 0
    assert not subprocess.check_output(['git', '--no-optional-locks', 'diff', '--cached', '--name-only'], cwd=root)
    m = manifest(root)
    tree = published_tree(root)
    source = {p: read(p) for p in SOURCE_PATHS}
    result = validate_source_bytes(source, root)
    expected = {**tree, **m['source_after_sha256']}
    from tests.b5_03_state import authorized_integration_paths
    generated, integration_additions = authorized_integration_paths(root, read)
    expected.update(generated)
    for path, digest in expected.items():
        raw = source[path] if path in source else read(path)
        assert sha(raw) == digest, 'Unrelated current file changed: ' + path
    portable_raw = (root / FIXTURES / 'portable_evidence_manifest.json').read_bytes()
    assert sha(portable_raw) == PORTABLE_INDEX_SHA256, 'Changed portable evidence inventory'
    portable = json.loads(portable_raw)
    assert portable['partial_archive'] is True and portable['original_archives_unchanged'] is True
    allowed_new = set(NEW_CODE_PATHS) | {
        FIXTURES + '/portable_evidence_manifest.json', 'tests/fixtures/batch_b_b5_02_endpoint.json',
    }
    allowed_new.update(integration_additions)
    for entry in portable['entries']:
        assert entry['path'].startswith(FIXTURES + '/')
        assert sha((root / entry['path']).read_bytes()) == entry['stored_sha256'], 'Changed portable input: ' + entry['path']
        allowed_new.add(entry['path'])
    assert sha((root / 'tests/fixtures/batch_b_b5_02_endpoint.json').read_bytes()) == 'e0ed1d9d2d6bee6c1b0846767f4d21eabb46278de09bbbdb07cab5cfc5cb1169'
    # The existing restoration contract includes five ordinary-untracked CSVs
    # as well as ignored inputs. Accept only their declared, exact bytes.
    from scripts.restore_historical_test_fixtures import legacy_entries, manifest_entries
    operational = {e['path']: e['sha256'] for e in legacy_entries(root) + manifest_entries(root)}
    for path, digest in operational.items():
        assert sha(read(path)) == digest, 'Changed operational fixture: ' + path
    untracked = subprocess.check_output(['git', '--no-optional-locks', 'ls-files', '--others', '--exclude-standard'], cwd=root, text=True).splitlines()
    assert set(untracked) <= allowed_new | set(operational), 'Undeclared additive path'
    # No new authoritative curated/manual/web path is permitted.
    for directory in ['data/curated', 'data/manual', 'web']:
        for path in (root / directory).rglob('*'):
            if not path.is_file():
                continue
            relative = str(path.relative_to(root))
            assert relative in expected or relative in operational, 'Undeclared current source: ' + relative
            if relative in operational:
                assert sha(read(relative)) == operational[relative], 'Changed operational fixture: ' + relative
    result['unchanged_other_tracked_files'] = len(tree) - len(SOURCE_PATHS) - len(set(generated) & set(tree))
    return result
