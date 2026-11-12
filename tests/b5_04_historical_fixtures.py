"""Route only authenticated predecessor operands of exact existing tests."""

import ast
from dataclasses import dataclass
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from scripts import audit_key_paper_coverage
from tests import b4_04_state, b5_03_historical_fixtures, b5_03_state
from tests.b5_04_published_inputs import BASE, build_published_inputs, sha256


MANIFEST = "fixtures/batch_b_b5_04_history_scopes.json"
MANIFEST_SHA256 = "df780e9c093cc69317b8c6208e84655e2bb4cef8cb911556044b66c9f99d8e24"
MANIFEST_PATH = Path(__file__).with_name("fixtures") / Path(MANIFEST).name
OLD_COUNT_SHA256 = "f16da75b85a094ff828e37bffbd20b031d29c130026517bec81d94efa9cac0b9"
MAPPINGS = "data/curated/author_institution_mappings.csv"
MAPPING_REPORT = "data/manual/missing_author_mappings_report.csv"
PUBLIC_CONTEXT = ("web/data/public_preview_papers.json", "web/data/public_preview_map_data.json")
SNAPSHOT = pytest.StashKey()


def authenticated_manifest(reader=None):
    assert (BASE, MANIFEST, MANIFEST_SHA256) == (
        "db1abff06d9ee077ae62421079059ee3af95607f",
        "fixtures/batch_b_b5_04_history_scopes.json",
        "df780e9c093cc69317b8c6208e84655e2bb4cef8cb911556044b66c9f99d8e24",
    ), "Unreviewed B5-04 routing metadata"
    assert MANIFEST_PATH == Path(__file__).parent / MANIFEST
    raw = (reader or Path.read_bytes)(MANIFEST_PATH)
    assert sha256(raw) == MANIFEST_SHA256, "Unreviewed B5-04 scope manifest"
    manifest = json.loads(raw)
    assert manifest["prior_commit"] == BASE
    return manifest


def authorized_scope(root, item, reader=None):
    manifest = authenticated_manifest(reader)
    route = manifest["scopes"].get(item.nodeid)
    if route is None:
        return None
    path = root / route["path"]
    assert Path(item.module.__file__).resolve() == path.resolve(), "Unexpected test module"
    raw = (reader or Path.read_bytes)(path)
    assert sha256(raw) == route["sha256"], "Changed scoped historical test"
    return route


def verify_actual_endpoint(root, reader=None):
    manifest = authenticated_manifest()
    read = reader or Path.read_bytes
    for relative, expected in manifest["successor_sha256"].items():
        assert sha256(read(root / relative)) == expected, "Changed actual B5-04 operand: " + relative


def historical_counts(snapshot):
    path = snapshot.root / "tests/baseline_expectations.py"
    raw = path.read_bytes()
    assert sha256(raw) == OLD_COUNT_SHA256, "Changed B5-03 count expectations"
    target = next(
        node.value for node in ast.parse(raw).body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == "CURRENT_CORPUS_COUNTS"
    )
    return ast.literal_eval(target)


@dataclass(frozen=True)
class SelectedPaths:
    """Allow named prior paths while leaving all other operands live."""

    current: Path
    prior: Path
    paths: tuple

    def __truediv__(self, child):
        relative = Path(child)
        assert not relative.is_absolute() and ".." not in relative.parts, "Historical input path must be repository-relative"
        selected = self.prior if relative.as_posix() in self.paths else self.current
        return selected / relative

    def __fspath__(self):
        return str(self.current)


def snapshot_for(config):
    existing = config.stash.get(SNAPSHOT, None)
    if existing is not None:
        return existing
    temp = TemporaryDirectory(prefix="b5-04-published-inputs-")
    try:
        view = build_published_inputs(config.rootpath, Path(temp.name) / "snapshot")
    except BaseException:
        temp.cleanup()
        raise
    config.stash[SNAPSHOT] = view
    config.add_cleanup(temp.cleanup)
    config.add_cleanup(view.verify)
    return view


def prior_call(function, current_root, snapshot_root):
    def called(root=current_root, *args, **kwargs):
        assert root in {current_root, snapshot_root}, "Unexpected historical reader root"
        return function(snapshot_root, *args, **kwargs)

    return called


def prior_context(function, current_root, snapshot_root):
    def called(root=current_root):
        assert root == current_root, "Unexpected historical context root"
        return function(SelectedPaths(current_root, snapshot_root, PUBLIC_CONTEXT))

    return called


def bind_route(scope, bindings, item, snapshot):
    root, prior, module = item.config.rootpath, snapshot.root, item.module
    for binding in bindings:
        if binding == "old_guard":
            scope.setattr(audit_key_paper_coverage, "ROOT", prior)
            scope.setattr(
                b4_04_state, "assert_current_state",
                prior_call(b4_04_state.assert_current_state, root, prior),
            )
        elif binding == "old_guard_root":
            scope.setattr(b4_04_state, "ROOT", prior)
        elif binding == "local151_source_overlay":
            scope.setattr(
                b5_03_historical_fixtures, "ROOT",
                SelectedPaths(root, prior, b4_04_state.SOURCE_PATHS),
            )
        elif binding == "old_report_and_paths":
            scope.setattr(audit_key_paper_coverage, "ROOT", prior)
            scope.setattr(
                b5_03_state, "authorized_integration_paths",
                prior_call(b5_03_state.authorized_integration_paths, root, prior),
            )
        elif binding == "old_projection":
            scope.setattr(
                b5_03_state, "verify_public_projection",
                prior_call(b5_03_state.verify_public_projection, root, prior),
            )
        elif binding == "test_r_snapshot":
            scope.setattr(module, "R", prior)
        elif binding == "test_root_mappings":
            scope.setattr(module, "ROOT", SelectedPaths(root, prior, (MAPPINGS,)))
        elif binding == "test_root_mapping_report":
            scope.setattr(module, "ROOT", SelectedPaths(root, prior, (MAPPING_REPORT,)))
        elif binding == "test_r_mapping_report":
            scope.setattr(module, "R", SelectedPaths(root, prior, (MAPPING_REPORT,)))
        elif binding == "test_old_map_context":
            scope.setattr(module, "load_context", prior_context(module.load_context, root, prior))
        elif binding == "test_old_counts":
            scope.setattr(module, "CURRENT_CORPUS_COUNTS", historical_counts(snapshot))
        else:
            raise AssertionError("Undeclared B5-04 historical route: " + binding)


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_protocol(item):
    route = authorized_scope(item.config.rootpath, item)
    if route is None:
        return (yield)
    verify_actual_endpoint(item.config.rootpath)
    snapshot = snapshot_for(item.config)
    try:
        with pytest.MonkeyPatch.context() as scope:
            bind_route(scope, route["bindings"], item, snapshot)
            return (yield)
    finally:
        verify_actual_endpoint(item.config.rootpath)
