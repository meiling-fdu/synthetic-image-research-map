"""Exact historical inputs for named B5-02 assertions; live B4-04 stays guarded.

No existing test, assertion, source reader or integrity helper is rewritten.
Only explicitly named prior-transaction contexts receive a versioned path.
"""
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path, PurePosixPath
import importlib
import io
import json
import subprocess
import tarfile
import pytest

from tests import b4_04_state as live

ROOT = Path(__file__).resolve().parents[1]
COMMIT = '2932b9a5b58a8c84761e381668925a765ca9719e'
ENDPOINT = 'tests/fixtures/batch_b_b5_02_endpoint.json'
ENDPOINT_SHA256 = 'e0ed1d9d2d6bee6c1b0846767f4d21eabb46278de09bbbdb07cab5cfc5cb1169'
PRIVATE_CONFIG = '[core]\nrepositoryformatversion = 0\nbare = false\nlogallrefupdates = false\n'
LOGICAL_INDEX_SHA256 = '9c0fc77bd384c758bc47f5c8ffa262f11061a2ae17c547b4055b290f45d775d3'
C_INPUTS = (
    'web/data/public_preview_papers.json', 'web/data/public_preview_map_data.json',
    'data/curated/paper_taxonomy.csv', 'data/curated/institutions.csv',
    'data/manual/neurips_2026_targeted_gap_fill_reconciliation.json',
    'data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json',
)
SCOPES = {
    'test_corpus_quality_batch_b_wave_b5_02': (
        'test_raw_prefix_and_every_actual_cell_delta',
        'test_authoritative_public_taxonomy_totals_match_exact_approved_evolution',
        'test_accounting_independent_original_ledger',
        'test_native_helper_double_submission_is_byte_and_timestamp_idempotent',
        'test_only_approved_authoritative_files_and_exact_source_bytes_change',
        'test_current_source_has_an_independent_exact_transaction_guard',
        'test_current_source_guard_rejects_tampering_independently_of_historical_success',
    ),
    'test_batch_b_historical_endpoints': (
        'test_snapshot_reader_has_no_mutable_current_source_fallback',
        'test_passing_historical_replay_does_not_authorize_current_source_corruption',
    ),
    'test_corpus_quality_batch_c_phase1': (
        'test_exact_approved_taxonomy_change',
        'test_recomputed_counts_and_registry_export_synchronization',
    ),
}


def authenticated_endpoint(root=ROOT):
    assert (COMMIT, ENDPOINT, ENDPOINT_SHA256, PRIVATE_CONFIG, LOGICAL_INDEX_SHA256) == (
        '2932b9a5b58a8c84761e381668925a765ca9719e',
        'tests/fixtures/batch_b_b5_02_endpoint.json',
        'e0ed1d9d2d6bee6c1b0846767f4d21eabb46278de09bbbdb07cab5cfc5cb1169',
        '[core]\nrepositoryformatversion = 0\nbare = false\nlogallrefupdates = false\n',
        '9c0fc77bd384c758bc47f5c8ffa262f11061a2ae17c547b4055b290f45d775d3',
    ), 'Unreviewed historical authorization metadata'
    raw = (root / ENDPOINT).read_bytes()
    assert live.sha(raw) == ENDPOINT_SHA256, 'Changed B5-02 endpoint manifest'
    value = json.loads(raw)
    assert value['commit'] == COMMIT and value['decision_rows'] == 138
    assert {k: list(v) for k, v in SCOPES.items()} == value['scope'], 'Unreviewed historical scope'
    return value


def endpoint_bytes(path, root=ROOT, reader=None):
    relative = PurePosixPath(path)
    assert not relative.is_absolute() and '..' not in relative.parts and str(relative) == path
    endpoint = authenticated_endpoint(root)
    tree = live.published_tree(root)
    assert path in tree, 'Undeclared historical path'
    read = reader or (lambda relative: live.published_bytes(relative, root))
    raw = read(path)
    assert live.sha(raw) == tree[path], 'Historical snapshot bytes changed: ' + path
    if path in endpoint['files']:
        assert live.sha(raw) == endpoint['files'][path]
    return raw


class PublishedInputPath:
    """Read-only root adapter for the original load_context(root) API."""
    def __init__(self, relative=''):
        self.relative = relative

    def __truediv__(self, child):
        relative = PurePosixPath(self.relative) / child
        assert not relative.is_absolute() and '..' not in relative.parts
        return PublishedInputPath(str(relative))

    def read_bytes(self):
        assert self.relative in C_INPUTS[:5], 'Undeclared historical context input'
        return endpoint_bytes(self.relative)

    def read_text(self, encoding='utf-8', errors='strict'):
        return self.read_bytes().decode(encoding, errors)

    def open(self, mode='r', encoding='utf-8', newline=None):
        assert mode in {'r', 'rt'}, 'Historical context inputs are read-only'
        return io.StringIO(self.read_text(encoding), newline=newline)


def historical_c_state():
    assert C_INPUTS == (
        'web/data/public_preview_papers.json', 'web/data/public_preview_map_data.json',
        'data/curated/paper_taxonomy.csv', 'data/curated/institutions.csv',
        'data/manual/neurips_2026_targeted_gap_fill_reconciliation.json',
        'data/raw/corpus_quality_audit_2026_10_04/batch_c_policy_decisions.json',
    ), 'Unreviewed historical context read set'
    endpoint = authenticated_endpoint()
    # Authenticate all six inputs before the unchanged parser sees any data.
    raw = {path: endpoint_bytes(path) for path in C_INPUTS}
    assert {p: live.sha(b) for p, b in raw.items()} == endpoint['c_context_input_sha256']
    from scripts.validate_corpus_quality_audit import load_context
    context = load_context(PublishedInputPath())
    ledger = json.loads(raw[C_INPUTS[-1]])
    return deepcopy((context, ledger))


def assert_historical_c_state(value):
    assert value == historical_c_state(), 'Changed historical Phase 1 state tuple'
    return True


class PublishedView:
    def __init__(self, root, tracked, operational):
        self.root = root
        self.tracked = dict(tracked)
        self.operational = dict(operational)
        self.index_sha256 = live.sha((root / '.git/index').read_bytes())

    def verify(self, reader=None):
        authenticated_endpoint()
        read = reader or (lambda path: (self.root / path).read_bytes())
        assert self.tracked == live.published_tree(), 'Changed historical inventory'
        from scripts.restore_historical_test_fixtures import legacy_entries, manifest_entries
        expected_operational = {e['path']: e['sha256'] for e in legacy_entries(ROOT) + manifest_entries(ROOT)}
        assert self.operational == expected_operational, 'Changed historical fixture metadata'
        assert read('.git/HEAD') == (COMMIT + '\n').encode(), 'Changed historical commit metadata'
        assert read('.git/config') == PRIVATE_CONFIG.encode(), 'Changed historical Git configuration'
        assert read('.git/objects/info/alternates') == (str(ROOT / '.git/objects') + '\n').encode(), 'Changed historical object reader'
        assert live.sha(read('.git/index')) == self.index_sha256, 'Changed historical index'
        logical = subprocess.check_output(['git', '--no-optional-locks', 'ls-files', '--stage', '-z'], cwd=self.root)
        assert live.sha(logical) == LOGICAL_INDEX_SHA256, 'Changed historical index entries'
        assert {str(p.relative_to(self.root / '.git')) for p in (self.root / '.git').rglob('*') if p.is_file()} == {
            'HEAD', 'config', 'index', 'objects/info/alternates'}, 'Undeclared historical Git metadata'
        for path, digest in {**self.tracked, **self.operational}.items():
            assert live.sha(read(path)) == digest, 'Changed historical view: ' + path
        assert len(live.rows(read(live.SOURCE_PATHS[2]))) == 138
        known = set(self.tracked) | set(self.operational)
        for directory in ['data', 'web']:
            for path in (self.root / directory).rglob('*'):
                if path.is_file():
                    assert str(path.relative_to(self.root)) in known, 'Undeclared historical input'
        return True


def build_view(root, destination):
    authenticated_endpoint(root)
    tree = live.published_tree(root)
    destination.mkdir()
    process = subprocess.Popen(['git', '--no-optional-locks', 'archive', '--format=tar', COMMIT],
                               cwd=root, stdout=subprocess.PIPE)
    assert process.stdout is not None
    with tarfile.open(fileobj=process.stdout, mode='r|') as archive:
        for entry in archive:
            target = (destination / entry.name).resolve()
            assert target.is_relative_to(destination.resolve())
            assert entry.isfile() or entry.isdir(), 'Unexpected historical archive link/type'
            archive.extract(entry, destination, filter='data')
    process.stdout.close()
    assert process.wait() == 0
    assert all(live.sha((destination / p).read_bytes()) == h for p, h in tree.items())
    # This metadata belongs only to the disposable historical view. Its object
    # reader points at the already authorized private clone, never the primary.
    metadata = destination / '.git'
    (metadata / 'objects/info').mkdir(parents=True)
    (metadata / 'refs').mkdir()
    common = Path(subprocess.check_output(['git', '--no-optional-locks', 'rev-parse', '--absolute-git-dir'], cwd=root, text=True).strip())
    assert common.resolve() == (root / '.git').resolve()
    (metadata / 'objects/info/alternates').write_text(str(common / 'objects') + '\n')
    (metadata / 'HEAD').write_text(COMMIT + '\n')
    (metadata / 'config').write_text(PRIVATE_CONFIG)
    subprocess.run(['git', '--no-optional-locks', 'read-tree', COMMIT], cwd=destination, check=True)
    from scripts.restore_historical_test_fixtures import restore
    restored = restore(destination)
    assert restored['verified_inputs'] == 117
    view = PublishedView(destination, tree, restored['sha256'])
    view.verify()
    return view


@pytest.fixture(scope='session')
def b5_02_published_view(tmp_path_factory):
    return build_view(ROOT, tmp_path_factory.mktemp('b5-02-published') / 'snapshot')


def authorized_scope(module, name):
    endpoint = authenticated_endpoint()
    basename = module.__name__.rsplit('.', 1)[-1]
    if basename not in SCOPES or name not in SCOPES[basename]:
        return None
    relative = 'tests/' + basename + '.py'
    assert Path(module.__file__).resolve() == (ROOT / relative).resolve()
    assert live.sha((ROOT / relative).read_bytes()) == endpoint['original_test_sha256'][relative], 'Changed scoped historical test'
    return basename


def pytest_generate_tests(metafunc):
    # Direct fixture-argument parametrization is scoped to these two functions.
    # The original module-scoped state fixture and every reader stay untouched.
    basename = metafunc.module.__name__.rsplit('.', 1)[-1]
    name = metafunc.function.__name__
    if basename == 'test_corpus_quality_batch_c_phase1' and name in SCOPES[basename]:
        assert authorized_scope(metafunc.module, name) == basename
        metafunc.parametrize('state', [historical_c_state()], ids=['published-2932b9a'], scope='function')


@contextmanager
def route_root(module, attribute, snapshot_root, monkeypatch):
    original = getattr(module, attribute)
    try:
        with monkeypatch.context() as scoped:
            scoped.setattr(module, attribute, snapshot_root)
            yield
    finally:
        assert getattr(module, attribute) == original, 'Historical scope leaked its root'


@pytest.fixture(autouse=True)
def exact_b5_02_historical_inputs(request, monkeypatch):
    name = getattr(request.node, 'originalname', None) or request.node.name.split('[', 1)[0]
    basename = request.module.__name__.rsplit('.', 1)[-1]
    if basename not in SCOPES:
        yield
        return
    scope = authorized_scope(request.module, name)
    if scope is None:
        yield
        return
    # The real current files must pass independently before historical inputs
    # can be selected, and again at teardown, including when a test fails.
    live.assert_current_state(ROOT)
    if scope == 'test_corpus_quality_batch_c_phase1':
        state = request.getfixturevalue('state')
        assert_historical_c_state(state)
        try:
            yield
        finally:
            assert_historical_c_state(state)
            live.assert_current_state(ROOT)
        return
    view = request.getfixturevalue('b5_02_published_view')
    view.verify()
    target = request.module
    attribute = 'R'
    if scope == 'test_corpus_quality_batch_b_wave_b5_02':
        pass
    elif name == 'test_snapshot_reader_has_no_mutable_current_source_fallback':
        attribute = 'ROOT'
    else:
        target = importlib.import_module('tests.test_corpus_quality_batch_b_wave_b5_02')
        assert live.sha(Path(target.__file__).read_bytes()) == authenticated_endpoint()['original_test_sha256']['tests/test_corpus_quality_batch_b_wave_b5_02.py']
    try:
        with route_root(target, attribute, view.root, monkeypatch):
            if name == 'test_current_source_guard_rejects_tampering_independently_of_historical_success':
                target.assert_source_transaction({p: (view.root / p).read_bytes() for p in live.SOURCE_PATHS})
            elif name == 'test_passing_historical_replay_does_not_authorize_current_source_corruption':
                # This family exercises the broader curated/manual guard.
                # Prove that exact guard passes before its injected read fault.
                target.test_only_approved_authoritative_files_and_exact_source_bytes_change()
            yield
    finally:
        view.verify()
        live.assert_current_state(ROOT)
