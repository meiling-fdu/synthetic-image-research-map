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
