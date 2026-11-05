"""Historical inputs cannot authorize changes to the actual B4-04 checkpoint."""
from copy import copy, deepcopy
from pathlib import Path
from types import SimpleNamespace
import csv
import io
import json
import pytest

from tests import b4_04_state as live
from tests import b5_02_historical_fixtures as history


def actual_source():
    return {p: (live.ROOT / p).read_bytes() for p in live.SOURCE_PATHS}


def encode_rows(original, records, *, header=True):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(live.rows(original)[0]), lineterminator='\n')
    if header:
        writer.writeheader()
    writer.writerows(records)
    return stream.getvalue().encode()


def test_immutable_138_and_actual_151_are_independently_valid(b5_02_published_view):
    view = b5_02_published_view
    assert view.verify()
    assert len(live.rows(history.endpoint_bytes(live.SOURCE_PATHS[2]))) == 138
    assert live.assert_current_state()['formal_decisions'] == 151
    from scripts.validate_corpus_quality_audit import load_context
    from collections import Counter
    totals = lambda root: Counter(t for r in load_context(root)['taxonomy'].values() for t in r['research_types'].split(';') if t)
    assert totals(view.root) == {'method': 578, 'dataset': 142, 'benchmark': 101, 'survey': 21, 'analysis_study': 86}
    assert totals(live.ROOT) == {'method': 578, 'dataset': 146, 'benchmark': 102, 'survey': 21, 'analysis_study': 90}


@pytest.mark.parametrize('field', ['COMMIT', 'ENDPOINT', 'ENDPOINT_SHA256', 'PRIVATE_CONFIG', 'SCOPES'])
def test_unreviewed_successor_metadata_is_rejected(monkeypatch, field):
    history.authenticated_endpoint()
    if field == 'SCOPES':
        value = deepcopy(history.SCOPES)
        value['test_corpus_quality_batch_b_wave_b5_02'] += ('arbitrary_test',)
    else:
        value = 'unreviewed'
    monkeypatch.setattr(history, field, value)
    with pytest.raises(AssertionError):
        history.authenticated_endpoint()


def test_recomputed_hash_cannot_authorize_a_changed_endpoint(tmp_path, monkeypatch):
    data = history.authenticated_endpoint()
    data['decision_rows'] = 151
    target = tmp_path / history.ENDPOINT
    target.parent.mkdir(parents=True)
    raw = (json.dumps(data) + '\n').encode()
    target.write_bytes(raw)
    monkeypatch.setattr(history, 'ENDPOINT_SHA256', live.sha(raw))
    with pytest.raises(AssertionError, match='authorization metadata'):
        history.authenticated_endpoint(tmp_path)


@pytest.mark.parametrize('field', ['BASE', 'MANIFEST_SHA256', 'TREE_SHA256', 'TREE_GZIP_SHA256', 'PORTABLE_INDEX_SHA256', 'NEW_CODE_PATHS'])
def test_unreviewed_current_state_authority_is_rejected(monkeypatch, field):
    live.manifest()
    monkeypatch.setattr(live, field, 'unreviewed')
    with pytest.raises(AssertionError):
        live.manifest()


@pytest.mark.parametrize('path', live.SOURCE_PATHS)
def test_changed_published_git_bytes_are_rejected(path):
    original = history.endpoint_bytes(path)
    with pytest.raises(AssertionError, match='Historical snapshot bytes changed'):
        history.endpoint_bytes(path, reader=lambda _: original + b'\nUNAUTHORIZED')


@pytest.mark.parametrize('path', [
    *live.SOURCE_PATHS, 'data/curated/institutions.csv',
    'data/curated/institution_locations.csv', 'data/curated/author_institution_mappings.csv',
    'web/data/public_preview_map_data.json', 'tests/public_refinement_snapshot.py',
])
def test_historical_pass_does_not_authorize_unrelated_current_changes(path):
    assert len(live.rows(history.endpoint_bytes(live.SOURCE_PATHS[2]))) == 138
    live.assert_current_state()
    def reader(relative):
        data = (live.ROOT / relative).read_bytes()
        return data + b'\nUNAUTHORIZED' if relative == path else data
    with pytest.raises(AssertionError):
        live.assert_current_state(reader=reader)


def test_original_decision_history_remains_an_exact_prefix():
    blobs = actual_source()
    live.validate_source_bytes(blobs)
    old_id = live.rows(live.published_bytes(live.SOURCE_PATHS[2]))[0]['decision_id'].encode()
    blobs[live.SOURCE_PATHS[2]] = blobs[live.SOURCE_PATHS[2]].replace(old_id, b'review:unauthorized', 1)
    with pytest.raises(AssertionError, match='original decision bytes'):
        live.validate_source_bytes(blobs)


@pytest.mark.parametrize('path', [
    'data/processed/neurips_2026_targeted_gap_fill_2026_10/staged/papers.csv',
    'data/processed/neurips_2026_targeted_gap_fill_2026_10/baseline_validation.log',
])
def test_declared_untracked_and_ignored_fixture_bytes_cannot_change(path):
    live.assert_current_state()
    def reader(relative):
        data = (live.ROOT / relative).read_bytes()
        return data + b'\nUNAUTHORIZED' if relative == path else data
    with pytest.raises(AssertionError, match='Changed operational fixture'):
        live.assert_current_state(reader=reader)


@pytest.mark.parametrize('rid', ['R045', 'R156', 'R251', 'R284', 'P251'])
def test_each_hold_cannot_be_silently_closed(rid):
    blobs = actual_source()
    live.validate_source_bytes(blobs)
    manifest = live.manifest()
    appended = [deepcopy(r['formal_decision']) for r in manifest['records']]
    target = next(i for i, r in enumerate(manifest['records']) if r['review_id'] == rid)
    assert appended[target]['action'] == 'unresolved'
    appended[target]['action'] = 'no_action_after_review'
    decision_path = live.SOURCE_PATHS[2]
    blobs[decision_path] = live.published_bytes(decision_path) + encode_rows(blobs[decision_path], appended, header=False)
    with pytest.raises(AssertionError):
        live.validate_source_bytes(blobs)


def test_P251_cannot_acquire_an_unauthorized_curated_author_row():
    blobs = actual_source()
    live.validate_source_bytes(blobs)
    case = next(r for r in live.manifest()['records'] if r['review_id'] == 'P251')
    records = live.rows(blobs[live.SOURCE_PATHS[0]])
    assert case['paper_id'] not in {r['paper_id'] for r in records}
    row = {k: '' for k in records[0]}
    row.update(paper_id=case['paper_id'], title=case['formal_decision']['title'], authors='Jia Chyi Ng')
    blobs[live.SOURCE_PATHS[0]] = encode_rows(blobs[live.SOURCE_PATHS[0]], [*records, row])
    with pytest.raises(AssertionError, match='identity or order'):
        live.validate_source_bytes(blobs)


def test_rehashed_author_binding_does_not_authorize_P251_edit():
    from tests.test_corpus_quality_batch_b_wave_b4_04 import CASES, accepted_case, canonical, sha
    case = deepcopy(CASES['P251'])
    old_hash = case['binding_sha256']
    case['binding']['canonical_bibliographic_identity']['authors'][0]['name'] = 'Jia Chyi Ng'
    case['binding_sha256'] = sha(canonical(case['binding']))
    case['formal_decision']['review_note'] = case['formal_decision']['review_note'].replace(old_hash, case['binding_sha256'])
    with pytest.raises(AssertionError):
        accepted_case(case)


@pytest.mark.parametrize('path', [
    *live.SOURCE_PATHS, 'data/processed/neurips_2026_targeted_gap_fill_2026_10/baseline_validation.log',
    '.git/HEAD', '.git/config', '.git/index', '.git/objects/info/alternates',
])
def test_historical_snapshot_and_metadata_tampering_is_rejected(b5_02_published_view, path):
    view = b5_02_published_view
    assert view.verify()
    def reader(relative):
        data = (view.root / relative).read_bytes()
        return data + b'\nUNAUTHORIZED' if relative == path else data
    with pytest.raises(AssertionError):
        view.verify(reader=reader)


@pytest.mark.parametrize('field', ['tracked', 'operational'])
def test_recomputed_view_metadata_cannot_replace_authority(b5_02_published_view, field):
    view = copy(b5_02_published_view)
    assert view.verify()
    value = dict(getattr(view, field))
    value[next(iter(value))] = '0' * 64
    setattr(view, field, value)
    with pytest.raises(AssertionError):
        view.verify()


def test_only_exact_reviewed_legacy_test_contexts_are_scoped():
    for basename, functions in history.SCOPES.items():
        module = SimpleNamespace(__name__='tests.' + basename, __file__=str(live.ROOT / 'tests' / (basename + '.py')))
        assert all(history.authorized_scope(module, name) == basename for name in functions)
        assert history.authorized_scope(module, 'unrelated_test') is None


def test_changed_original_test_cannot_receive_historical_scope(monkeypatch):
    basename = 'test_corpus_quality_batch_b_wave_b5_02'
    path = live.ROOT / 'tests' / (basename + '.py')
    module = SimpleNamespace(__name__='tests.' + basename, __file__=str(path))
    original = Path.read_bytes
    def reader(self):
        data = original(self)
        return data + b'\nUNREVIEWED TEST EDIT' if self == path else data
    monkeypatch.setattr(Path, 'read_bytes', reader)
    with pytest.raises(AssertionError, match='Changed scoped historical test'):
        history.authorized_scope(module, history.SCOPES[basename][0])


@pytest.mark.parametrize('failure', [False, True])
def test_root_routing_restores_globals_after_success_and_exception(monkeypatch, tmp_path, failure):
    module = SimpleNamespace(R=live.ROOT)
    if failure:
        with pytest.raises(RuntimeError, match='controlled test failure'):
            with history.route_root(module, 'R', tmp_path, monkeypatch):
                assert module.R == tmp_path
                raise RuntimeError('controlled test failure')
    else:
        with history.route_root(module, 'R', tmp_path, monkeypatch):
            assert module.R == tmp_path
    assert module.R == live.ROOT


def test_nested_scope_restoration_is_independent(monkeypatch, tmp_path):
    module = SimpleNamespace(ROOT=live.ROOT)
    one, two = tmp_path / 'one', tmp_path / 'two'
    with history.route_root(module, 'ROOT', one, monkeypatch):
        assert module.ROOT == one
        with history.route_root(module, 'ROOT', two, monkeypatch):
            assert module.ROOT == two
        assert module.ROOT == one
    assert module.ROOT == live.ROOT


def test_unselected_functions_keep_the_actual_current_root():
    from tests import test_corpus_quality_batch_b_wave_b5_02 as original
    assert history.authorized_scope(original, 'test_required_caveats_are_preserved_separately_from_acceptance') is None
    assert original.R == live.ROOT


def test_historical_phase1_state_matches_the_complete_original_parser(b5_02_published_view):
    from collections import Counter
    from scripts.validate_corpus_quality_audit import load_context
    context, ledger = history.historical_c_state()
    assert context == load_context(b5_02_published_view.root)
    assert isinstance(context['pairs'], Counter)
    assert all(isinstance(context[k], set) for k in ['institutions', 'frozen', 'formal', 'unmapped'])
    assert ledger == json.loads((b5_02_published_view.root / history.C_INPUTS[-1]).read_bytes())
    pid = 'curated:14272073fa5bc0e301b5'
    assert context['taxonomy'][pid]['research_types'] == 'method'
    assert load_context(live.ROOT)['taxonomy'][pid]['research_types'] == 'method;dataset'
    assert history.assert_historical_c_state((context, ledger))


@pytest.mark.parametrize('damage', ['taxonomy', 'ledger', 'mutable_current_context'])
def test_historical_phase1_tuple_cannot_be_redefined(damage):
    value = history.historical_c_state()
    if damage == 'taxonomy':
        value[0]['taxonomy']['curated:14272073fa5bc0e301b5']['research_types'] = 'method;dataset'
    elif damage == 'ledger':
        value[1]['policies'][0]['final_rule'] = 'unreviewed'
    else:
        from scripts.validate_corpus_quality_audit import load_context
        value = (load_context(live.ROOT), value[1])
    with pytest.raises(AssertionError, match='historical Phase 1 state tuple'):
        history.assert_historical_c_state(value)


def test_phase1_context_copy_and_read_only_inputs(monkeypatch):
    one, two = history.historical_c_state(), history.historical_c_state()
    assert one == two and one is not two and one[0] is not two[0]
    one[0]['counts']['public'] = 0
    assert history.assert_historical_c_state(two)
    with pytest.raises(AssertionError, match='read-only'):
        history.PublishedInputPath(history.C_INPUTS[0]).open('w')
    monkeypatch.setattr(history, 'C_INPUTS', history.C_INPUTS + ('unreviewed.json',))
    with pytest.raises(AssertionError, match='read set'):
        history.historical_c_state()


def test_phase1_input_corruption_is_rejected_before_parsing(monkeypatch):
    original = history.endpoint_bytes
    damaged = history.C_INPUTS[2]
    def reader(path, *args, **kwargs):
        raw = original(path, *args, **kwargs)
        return raw + b'\nNOT CSV' if path == damaged else raw
    monkeypatch.setattr(history, 'endpoint_bytes', reader)
    with pytest.raises(AssertionError):
        history.historical_c_state()


def test_only_two_phase1_functions_receive_direct_historical_state():
    from tests import test_corpus_quality_batch_c_phase1 as original
    captured = []
    def parameterize(*args, **kwargs):
        captured.append((args, kwargs))
    for name in history.SCOPES['test_corpus_quality_batch_c_phase1']:
        history.pytest_generate_tests(SimpleNamespace(module=original, function=getattr(original, name), parametrize=parameterize))
    assert len(captured) == 2
    assert all(args[0] == 'state' and len(args[1]) == 1 and kwargs['scope'] == 'function' for args, kwargs in captured)
    assert all(history.assert_historical_c_state(args[1][0]) for args, _ in captured)
    history.pytest_generate_tests(SimpleNamespace(module=original, function=original.test_policy_lock_and_exact_reconciliation, parametrize=parameterize))
    assert len(captured) == 2
