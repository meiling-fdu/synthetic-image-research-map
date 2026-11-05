"""Actual B5-03 publication, finite historical scopes and negative boundaries."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import json
import pytest
from tests import b4_04_state as live
from tests import b5_03_state as integration
from tests import b5_03_historical_fixtures as history


def test_actual151_decisions_and_only_reviewed_source_delta():
    result = live.assert_current_state()
    assert result == {'formal_decisions': 151, 'appended': 13, 'changed_cells': 56,
                      'unchanged_other_tracked_files': 4824}


def test_current_report_is_canonical_and_repeatable():
    from scripts.audit_key_paper_coverage import expected_artifacts, validate_artifacts
    assert expected_artifacts(live.ROOT) == expected_artifacts(live.ROOT)
    assert validate_artifacts(live.ROOT) == []
    paths, additions = integration.authorized_integration_paths()
    assert len(set(paths) & set(live.published_tree())) == 5
    assert set(additions) == set(integration.authenticated_descriptor()['additions'])


def test_export_projection_and_all_optional_identity_omissions():
    result = integration.verify_public_projection()
    assert result == {'paper_records': 674, 'map_records': 1410, 'changed_papers': 8,
                      'changed_markers': 23, 'missing_optional_paper_id': 164}


def test_canonical_identity_matcher_handles_absent_optional_paper_id():
    from scripts.curated_export import PaperIdentityCache, PaperIdentityIndex
    from tests import b5_02_historical_fixtures as published
    records = json.loads(published.endpoint_bytes('web/data/public_preview_papers.json'))['records']
    index = PaperIdentityIndex(records, PaperIdentityCache())
    missing = [r for r in records if 'paper_id' not in r]
    assert len(missing) == 164
    assert all(integration.unique_match(index, row) is row for row in missing)
    # A copied row with the same DOI/identity is a distinct ambiguous candidate.
    duplicate = deepcopy(missing[0])
    ambiguous = PaperIdentityIndex([missing[0], duplicate], PaperIdentityCache())
    with pytest.raises(AssertionError, match='Ambiguous or missing canonical identity'):
        integration.unique_match(ambiguous, missing[0])
    empty = PaperIdentityIndex([], PaperIdentityCache())
    with pytest.raises(AssertionError, match='Ambiguous or missing canonical identity'):
        integration.unique_match(empty, missing[0])


def test_reordered_records_cannot_be_accepted_by_position_alone():
    papers = json.loads((live.ROOT / 'web/data/public_preview_papers.json').read_bytes())
    papers['records'][0], papers['records'][1] = papers['records'][1], papers['records'][0]
    def read(path):
        return json.dumps(papers).encode() if path == 'web/data/public_preview_papers.json' else (live.ROOT / path).read_bytes()
    integration.verify_public_projection()
    with pytest.raises(AssertionError):
        integration.verify_public_projection(read=read)


def test_current_public_and_source_counts_and_expectations_agree():
    from scripts.validate_corpus_quality_audit import load_context
    from tests.baseline_expectations import RESEARCH_TYPE_TOTALS, TASK_TOTALS
    context = load_context(live.ROOT)
    assert context['counts'] == live.manifest()['public_invariants']
    source = Counter(x for row in context['taxonomy'].values() for x in row['research_types'].split(';') if x)
    papers = json.loads((live.ROOT / 'web/data/public_preview_papers.json').read_bytes())['records']
    assert source == Counter(x for p in papers for x in p['research_types']) == RESEARCH_TYPE_TOTALS == {
        'method': 578, 'dataset': 146, 'benchmark': 102, 'survey': 21, 'analysis_study': 90}
    assert Counter(x for p in papers for x in p['tasks']) == TASK_TOTALS == {
        'detection': 621, 'source_attribution': 84, 'localization': 45}


def test_original_historical_report_snapshots_remain_immutable():
    assert live.sha(live.published_bytes('docs/key_paper_coverage_report.md')) == 'e3f92feea95ab5464d59060741e7356c419cac71068ab5af2afefaa913fb5f86'
    assert live.sha(live.published_bytes('data/manual/key_paper_coverage_report.csv')) == 'dbe1bd75e8d619a3a28354df1bccd79037f0aa281de49a37bbb49d3937d75099'


@pytest.mark.parametrize('path', [
    *live.SOURCE_PATHS, 'docs/key_paper_coverage_report.md', 'data/manual/key_paper_coverage_report.csv',
    'docs/public_preview_report.md', 'web/data/public_preview_papers.json', 'web/data/public_preview_map_data.json',
    'scripts/audit_key_paper_coverage.py', 'scripts/export_public_preview.py', 'web/app.js',
    'tests/baseline_expectations.py', 'tests/test_corpus_quality_batch_b_wave_b5_02.py',
    'tests/b5_03_historical_fixtures.py', 'data/curated/institutions.csv',
])
def test_historical_success_never_authorizes_current_tampering(path):
    live.assert_current_state()
    def read(relative):
        return (live.ROOT / relative).read_bytes() + (b'\nUNAUTHORIZED' if relative == path else b'')
    with pytest.raises(AssertionError):
        live.assert_current_state(reader=read)


@pytest.mark.parametrize('field', ['outputs', 'inputs', 'baseline', 'source_manifest', 'historical_scopes', 'payload_sha256', 'replacements'])
def test_recomputed_descriptor_hash_cannot_expand_authorization(field, monkeypatch):
    integration.authorized_integration_paths()
    value = deepcopy(integration.authenticated_descriptor())
    value[field] = 'UNREVIEWED'
    raw = json.dumps(value).encode()
    def read(path):
        return raw if path == integration.DESCRIPTOR else (live.ROOT / path).read_bytes()
    with pytest.raises(AssertionError, match='Unreviewed B5-03 endpoint'):
        integration.authorized_integration_paths(read=read)
    with monkeypatch.context() as scoped:
        scoped.setattr(integration, 'DESCRIPTOR_SHA256', integration.sha(raw))
        with pytest.raises(AssertionError, match='Unreviewed B5-03 authorization metadata'):
            integration.authorized_integration_paths(read=read)


def test_three_exact_historical_assertions_and_expectation_pairing_only():
    functions = []
    for basename, scope in history.SCOPES.items():
        module = SimpleNamespace(__name__='tests.' + basename, __file__=str(live.ROOT / 'tests' / (basename + '.py')))
        for name in scope['functions']:
            assert history.authorized_scope(module, name) == scope['view']
            functions.append(name)
        assert history.authorized_scope(module, 'unrelated_test') is None
    assert len(functions) == 4  # Three new path-scoped assertions, plus one existing expectation pairing.
    from tests import test_corpus_quality_batch_b_wave_b5_02 as original
    assert original.R == live.ROOT
    assert history.authorized_scope(original, 'test_required_caveats_are_preserved_separately_from_acceptance') is None


def test_unreviewed_historical_scope_metadata_is_rejected(monkeypatch):
    from tests import test_corpus_quality_batch_b_wave_b5_02 as module
    name = 'test_public_projection_updates_exactly_six_papers_and_fourteen_dependents'
    assert history.authorized_scope(module, name)
    changed = deepcopy(history.SCOPES)
    changed[module.__name__.rsplit('.', 1)[-1]]['functions'] += ('arbitrary_test',)
    with monkeypatch.context() as scoped:
        scoped.setattr(history, 'SCOPES', changed)
        with pytest.raises(AssertionError, match='Unreviewed B5-03 historical scope'):
            history.authorized_scope(module, name)


def test_changed_original_assertion_cannot_receive_historical_inputs(monkeypatch):
    from tests import test_corpus_quality_batch_b_wave_b5_02 as module
    name = 'test_public_projection_updates_exactly_six_papers_and_fourteen_dependents'
    assert history.authorized_scope(module, name)
    original = Path.read_bytes
    target = Path(module.__file__)
    def read(path):
        raw = original(path)
        return raw + b'\nALTERED ASSERTION' if path == target else raw
    with monkeypatch.context() as scoped:
        scoped.setattr(Path, 'read_bytes', read)
        with pytest.raises(AssertionError, match='Changed B5-03 scoped test'):
            history.authorized_scope(module, name)


def test_local151_and_published138_are_distinct_authenticated_checkpoints(b4_04_local151_view, b5_02_published_view):
    local, published = b4_04_local151_view, b5_02_published_view
    assert local.root != published.root and local.verify() and published.verify()
    assert len(live.rows((local.root / live.SOURCE_PATHS[2]).read_bytes())) == 151
    assert len(live.rows((published.root / live.SOURCE_PATHS[2]).read_bytes())) == 138
    assert (local.root / 'web/data/public_preview_papers.json').read_bytes() == (published.root / 'web/data/public_preview_papers.json').read_bytes()
    with pytest.raises(AssertionError):
        history.Local151View(published).verify()


@pytest.mark.parametrize('path', [*live.SOURCE_PATHS, 'web/data/public_preview_papers.json', 'web/data/public_preview_map_data.json', '.git/HEAD', '.git/index', '.git/objects/info/alternates'])
def test_local151_snapshot_source_export_and_metadata_tampering_rejected(b4_04_local151_view, path):
    view = b4_04_local151_view
    assert view.verify()
    def read(relative):
        return (view.root / relative).read_bytes() + (b'\nUNAUTHORIZED' if relative == path else b'')
    with pytest.raises(AssertionError):
        view.verify(reader=read)


@pytest.mark.parametrize('failure', [False, True])
def test_historical_expectation_scope_restores_global_identity(monkeypatch, failure):
    from tests.baseline_expectations import CURRENT_TAXONOMY_TOTALS
    module = SimpleNamespace(CURRENT_TAXONOMY_TOTALS=CURRENT_TAXONOMY_TOTALS)
    old = history.historical_current_totals()
    assert old['dataset'] == 142 and old['benchmark'] == 101 and old['analysis_study'] == 86
    if failure:
        with pytest.raises(RuntimeError):
            with history.route_historical_expectations(module, monkeypatch):
                assert module.CURRENT_TAXONOMY_TOTALS == old
                raise RuntimeError('controlled failure')
    else:
        with history.route_historical_expectations(module, monkeypatch):
            assert module.CURRENT_TAXONOMY_TOTALS == old
    assert module.CURRENT_TAXONOMY_TOTALS is CURRENT_TAXONOMY_TOTALS
    assert CURRENT_TAXONOMY_TOTALS['dataset'] == 146


def test_changed_historical_constants_and_mutated_expectation_data_rejected(monkeypatch):
    from tests import b5_02_historical_fixtures as published
    path = 'tests/baseline_expectations.py'
    history.historical_current_totals()
    with pytest.raises(AssertionError, match='Changed historical baseline constants'):
        history.historical_current_totals(reader=lambda p: published.endpoint_bytes(p) + b'\nUNAUTHORIZED')
    original = {'unchanged': True}
    module = SimpleNamespace(CURRENT_TAXONOMY_TOTALS=original)
    with pytest.raises(AssertionError, match='Changed historical expectation data'):
        with history.route_historical_expectations(module, monkeypatch):
            module.CURRENT_TAXONOMY_TOTALS['dataset'] = 0
    assert module.CURRENT_TAXONOMY_TOTALS is original
