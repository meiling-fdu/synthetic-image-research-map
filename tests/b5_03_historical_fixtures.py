"""Finite prior-transaction inputs alongside the actual B5-03 publication state."""
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
import ast
import pytest

from tests import b4_04_state as live
from tests import b5_02_historical_fixtures as history
from tests import b5_03_state as integration

ROOT = Path(__file__).resolve().parents[1]
SCOPES = {
    'test_corpus_quality_batch_b_wave_b4_04': {
        'sha256': '2dca0104c44e3bb1108f2de80434ba1bd0631f9abf24ba0c5f0321f887fb89d1',
        'view': 'M82_LOCAL151_CHECKPOINT',
        'functions': (
            'test_recomputed_source_totals_and_unchanged_public_identities_and_relationships',
            'test_all_other_curated_manual_raw_and_website_paths_unchanged',
        ),
    },
    'test_corpus_quality_batch_b_wave_b5_02': {
        'sha256': '7648eeedebd42fbf8188b17964fa9358cc68e451f10e0681d2d1648c6252c835',
        'view': 'PUBLISHED2932_138',
        'functions': ('test_public_projection_updates_exactly_six_papers_and_fourteen_dependents',),
    },
    'test_corpus_quality_batch_c_phase1': {
        'sha256': '9293d5c8e5062ea1d1f46a0da4e0ff6355046b1e2212b593b34b9d46afd3166e',
        'view': 'PUBLISHED2932_EXPECTATIONS_ONLY',
        'functions': ('test_recomputed_counts_and_registry_export_synchronization',),
    },
}


def authorized_scope(module, name):
    basename = module.__name__.rsplit('.', 1)[-1]
    if basename not in SCOPES or name not in SCOPES[basename]['functions']:
        return None
    descriptor = integration.authenticated_descriptor()
    serial = {k: {**v, 'functions': list(v['functions'])} for k, v in SCOPES.items()}
    assert serial == descriptor['historical_scopes'], 'Unreviewed B5-03 historical scope'
    path = ROOT / 'tests' / (basename + '.py')
    assert Path(module.__file__).resolve() == path.resolve()
    assert live.sha(path.read_bytes()) == SCOPES[basename]['sha256'], 'Changed B5-03 scoped test'
    return SCOPES[basename]['view']


def historical_current_totals(reader=None):
    path = 'tests/baseline_expectations.py'
    read = reader or history.endpoint_bytes
    raw = read(path)
    assert live.sha(raw) == 'a3784c28227fe60aba50678a8690f4ede5005fd99f6e3e41d8c090981fab8fcb', 'Changed historical baseline constants'
    definitions = {
        node.targets[0].id: node.value for node in ast.parse(raw).body
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
    }
    tasks = ast.literal_eval(definitions['TASK_TOTALS'])
    types = ast.literal_eval(definitions['RESEARCH_TYPE_TOTALS'])
    assert ast.dump(definitions['CURRENT_TAXONOMY_TOTALS'], include_attributes=False) == ast.dump(
        ast.parse('{**TASK_TOTALS, **RESEARCH_TYPE_TOTALS}', mode='eval').body, include_attributes=False)
    return {**tasks, **types}


@contextmanager
def route_historical_expectations(module, monkeypatch):
    previous = module.CURRENT_TAXONOMY_TOTALS
    expected = historical_current_totals()
    supplied = deepcopy(expected)
    try:
        with monkeypatch.context() as scoped:
            scoped.setattr(module, 'CURRENT_TAXONOMY_TOTALS', supplied)
            try:
                yield
            finally:
                assert supplied == expected, 'Changed historical expectation data'
    finally:
        assert module.CURRENT_TAXONOMY_TOTALS is previous


class Local151View:
    """The sealed B4 local checkpoint, separate from the 138-row publication."""
    def __init__(self, published):
        self.published = published
        self.root = published.root

    def verify(self, reader=None):
        read = reader or (lambda path: (self.root / path).read_bytes())
        sources = {path: read(path) for path in live.SOURCE_PATHS}
        result = live.validate_source_bytes(sources)
        assert result == {'formal_decisions': 151, 'appended': 13, 'changed_cells': 56}
        # Authenticate each reviewed replacement before the original complete
        # published-view verifier sees its immutable predecessor bytes.
        def published_reader(path):
            if path in sources:
                return history.endpoint_bytes(path)
            return read(path)
        assert self.published.verify(reader=published_reader)
        return True


@pytest.fixture(scope='session')
def b4_04_local151_view(tmp_path_factory):
    live.assert_current_state()
    published = history.build_view(ROOT, tmp_path_factory.mktemp('b5-03-b4-local') / 'snapshot')
    manifest = live.manifest()
    for path in live.SOURCE_PATHS:
        raw = (ROOT / path).read_bytes()
        assert live.sha(raw) == manifest['source_after_sha256'][path]
        (published.root / path).write_bytes(raw)
    view = Local151View(published)
    view.verify()
    return view


@pytest.fixture(autouse=True)
def exact_b5_03_prior_transaction_inputs(request, monkeypatch, exact_b5_02_historical_inputs):
    # The original B5-02 fixture remains in force first, with its eleven exact
    # functions and thirty-three cases unchanged.
    role = authorized_scope(request.module, request.function.__name__)
    if role is None:
        yield
        return
    live.assert_current_state()
    if role == 'PUBLISHED2932_EXPECTATIONS_ONLY':
        try:
            with route_historical_expectations(request.module, monkeypatch):
                yield
        finally:
            live.assert_current_state()
        return
    fixture_name = 'b4_04_local151_view' if role == 'M82_LOCAL151_CHECKPOINT' else 'b5_02_published_view'
    view = request.getfixturevalue(fixture_name)
    view.verify()
    try:
        with history.route_root(request.module, 'R', view.root, monkeypatch):
            yield
    finally:
        view.verify()
        live.assert_current_state()
