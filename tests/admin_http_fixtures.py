"""Temporary input contexts for the original admin HTTP lifecycle tests.

These fixtures retain the published test sources, real parsers, HTTP handlers,
queue computations, durable writes and Git subprocess. Only unrelated live
repository inputs are replaced by small files in each test's temporary directory.
"""

import contextlib
import csv
import functools
import json
from pathlib import Path
import subprocess
import sys
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from scripts import admin_review_queues, serve_admin


@contextlib.contextmanager
def institution_public_inputs(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    public = {"paper_id": "paper:1", "title": "Example paper",
              "institution_id": "institution:correct"}
    papers, markers = root / "public_papers.json", root / "public_map.json"
    hierarchy = root / "hierarchy.csv"
    for path in (papers, markers):
        path.write_text(json.dumps([public]), encoding="utf-8")
    hierarchy.write_text("child_institution_id,parent_institution_id\n", encoding="utf-8")
    with (
        patch.object(serve_admin, "PUBLIC_PAPERS_PATH", papers),
        patch.object(serve_admin, "PUBLIC_MAP_PATH", markers),
        patch.object(serve_admin, "INSTITUTION_HIERARCHY_PATH", hierarchy),
    ):
        yield


def isolated_metadata_server(original):
    """Add explicit inputs around the unchanged metadata-server factory."""
    @functools.wraps(original)
    @contextlib.contextmanager
    def server(self, directory, *args, **kwargs):
        metadata_tests = sys.modules[original.__module__]

        directory = Path(directory)
        public_papers = directory / "public_papers.json"
        public_map = directory / "public_map.json"
        candidate_map = directory / "candidate_map.json"
        candidate_map.write_text("[]", encoding="utf-8")
        read_queue_json = admin_review_queues.read_json
        public_paths = {
            admin_review_queues.DEFAULT_PUBLIC_PAPERS_PATH: public_papers,
            admin_review_queues.DEFAULT_PUBLIC_MAP_PATH: public_map,
        }

        def read_fixture_json(path):
            # Defaults in ReviewContext are definition-bound; dashboard_data
            # reads the same paths directly. Both still use the real parser.
            return read_queue_json(public_paths.get(path, path))

        load_fixture_admin = functools.partial(
            serve_admin.load_admin_data,
            curated_mappings_path=directory / "author_institution_mappings.csv",
            canonical_candidate_map_path=candidate_map,
        )
        diagnostic_paths = {
            name: directory / (name + ".csv")
            for name in admin_review_queues.QUEUE_PATHS
        }
        for path in diagnostic_paths.values():
            with path.open("w", encoding="utf-8", newline="") as handle:
                csv.DictWriter(handle, fieldnames=("paper_id", "title", "institution")).writeheader()

        # Exercise actual Git status, scoped to the fixture rather than to an
        # evolving developer checkout. No commit or network operation is needed.
        subprocess.run(
            ("git", "init", "--quiet", str(directory)),
            check=True, capture_output=True, text=True,
        )
        with (
            patch.object(admin_review_queues, "read_json", read_fixture_json),
            patch.object(admin_review_queues, "QUEUE_PATHS", diagnostic_paths),
            patch.object(admin_review_queues, "MANUAL_DIR", directory),
            patch.object(admin_review_queues, "REPOSITORY_ROOT", directory),
            patch.object(serve_admin, "load_admin_data", load_fixture_admin),
            patch.object(metadata_tests, "load_admin_data", load_fixture_admin),
            patch("scripts.admin_workflows.REPOSITORY_ROOT", directory),
        ):
            with original(self, directory, *args, **kwargs) as result:
                yield result

    return server


class JoinedFixtureHTTPServer(ThreadingHTTPServer):
    """Join active request workers before the test removes its CSV files."""

    daemon_threads = False
    block_on_close = True


@contextlib.contextmanager
def mapping_registration_inputs(root, endpoint_module):
    """Copy only the existing endpoint identity; preserve all its source fields."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    seed = {"paper_id": "openalex:W4416604008"}
    keys = set(serve_admin.identity_keys(seed))

    def matches(row):
        return bool(keys.intersection(serve_admin.identity_keys(row)))

    # Preparation happens before the HTTP client starts. The selected identity
    # is an excluded curated record; retain its actual exclusion and taxonomy.
    with serve_admin.CURATED_PAPERS_PATH.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = reader.fieldnames
        selected = [row for row in reader if matches(row)]
    assert len(selected) == 1, "Endpoint fixture identity must be unique"
    keys.update(serve_admin.identity_keys(selected[0]))
    papers = root / "papers.csv"
    with papers.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(selected)
    exclusions = root / "exclusions.csv"
    with serve_admin.CURATED_EXCLUSIONS_PATH.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        exclusion_columns = reader.fieldnames
        selected_exclusions = [row for row in reader if matches(row)]
    with exclusions.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=exclusion_columns)
        writer.writeheader()
        writer.writerows(selected_exclusions)

    public_paths = {}
    for source, name in (
        (serve_admin.PUBLIC_PAPERS_PATH, "public.json"),
        (serve_admin.PUBLIC_MAP_PATH, "markers.json"),
        (serve_admin.CANONICAL_CANDIDATE_MAP_PATH, "candidates.json"),
    ):
        records = [row for row in serve_admin.read_json_records(source) if matches(row)]
        target = root / name
        target.write_text(json.dumps(records), encoding="utf-8")
        public_paths[name] = target

    original_handler = endpoint_module.make_handler
    original_loader = serve_admin.load_admin_data
    with contextlib.ExitStack() as stack:
        stack.enter_context(patch.object(serve_admin, "PUBLIC_PAPERS_PATH", public_paths["public.json"]))
        stack.enter_context(patch.object(serve_admin, "PUBLIC_MAP_PATH", public_paths["markers.json"]))
        stack.enter_context(patch.object(endpoint_module, "ThreadingHTTPServer", JoinedFixtureHTTPServer))

        def fixture_handler(*args, **kwargs):
            kwargs["curated_papers_path"] = papers
            kwargs["exclusions_path"] = exclusions
            stack.enter_context(patch.object(serve_admin, "load_admin_data", functools.partial(
                original_loader, curated_mappings_path=kwargs["mappings_path"],
                canonical_candidate_map_path=public_paths["candidates.json"],
            )))
            # Establish the fixture's real admin identity and initialize the
            # shared read-only venue catalog before starting a timed request.
            # The HTTP route still executes this loader and all actual writes.
            _, initial = serve_admin.load_admin_data(exclusions, papers)
            assert seed["paper_id"] in initial["papers_by_id"]
            assert initial["papers_by_id"][seed["paper_id"]]["has_active_exclusion"]
            return original_handler(*args, **kwargs)

        stack.enter_context(patch.object(endpoint_module, "make_handler", fixture_handler))
        yield {"paper": selected[0], "exclusions": selected_exclusions}
