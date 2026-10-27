"""Keep tiny HTTP lifecycle fixtures independent of the growing live corpus."""

import csv
import json
from pathlib import Path
import tempfile
import unittest

from scripts import admin_review_queues, admin_workflows, serve_admin
from tests import test_institution_cleanup_queue as cleanup_tests
from tests import test_paper_metadata_editing as metadata_tests
from tests.admin_http_fixtures import institution_public_inputs


LIVE_CORPUS_PATHS = frozenset({
        serve_admin.PUBLIC_PAPERS_PATH,
        serve_admin.PUBLIC_MAP_PATH,
        serve_admin.CANONICAL_CANDIDATE_MAP_PATH,
        serve_admin.CURATED_MAPPINGS_PATH,
        serve_admin.INSTITUTION_HIERARCHY_PATH,
        *admin_review_queues.QUEUE_PATHS.values(),
        admin_review_queues.DEFAULT_PUBLIC_PAPERS_PATH,
        admin_review_queues.DEFAULT_PUBLIC_MAP_PATH,
})


def block_live_corpus(monkeypatch):
    """Fail on escaped fixture reads, rather than mocking parser/queue results."""
    original_open = Path.open

    def guarded_open(path, *args, **kwargs):
        if path in LIVE_CORPUS_PATHS:
            raise AssertionError(f"HTTP fixture escaped into the live corpus: {path}")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded_open)


def test_cleanup_http_lifecycle_does_not_read_live_public_corpus(monkeypatch, tmp_path):
    block_live_corpus(monkeypatch)
    case = cleanup_tests.InstitutionCleanupQueueTests(
        "test_visible_open_confirmed_change_resolves_through_admin_http"
    )
    result = unittest.TestResult()
    with institution_public_inputs(tmp_path):
        case.run(result)
    assert result.testsRun == 1
    assert not result.errors, result.errors
    assert not result.failures, result.failures


def test_metadata_dashboard_uses_fixture_records_mappings_and_real_git(monkeypatch):
    block_live_corpus(monkeypatch)
    helper = metadata_tests.PaperMetadataEditingTests()
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        original_popen = admin_workflows.subprocess.Popen
        git_calls = []

        def fixture_popen(command, *args, **kwargs):
            if tuple(command) == ("git", "status", "--short"):
                assert kwargs.get("cwd") == root
                git_calls.append(tuple(command))
            return original_popen(command, *args, **kwargs)

        monkeypatch.setattr(admin_workflows.subprocess, "Popen", fixture_popen)
        with helper.metadata_server(
            root, [], original_overrides={
                "publication_type": "conference", "venue": "Unknown proceedings",
            },
        ) as (base, original, path, _links, _identifier):
            public = {
                **original, "id": original["paper_id"],
                "institution": "Fixture University",
                "institution_id": "institution:fixture",
            }
            (root / "public_papers.json").write_text(json.dumps([public]), encoding="utf-8")
            (root / "public_map.json").write_text(json.dumps([public]), encoding="utf-8")
            mapping = {
                column: "" for column in metadata_tests.AUTHOR_INSTITUTION_MAPPING_COLUMNS
            }
            mapping.update({
                "mapping_id": "mapping:fixture",
                "paper_id": original["paper_id"],
                "title": original["title"],
                "institution": "Fixture University",
                "institution_id": "institution:fixture",
                "mapping_status": "active",
            })
            with (root / "author_institution_mappings.csv").open(
                "w", encoding="utf-8", newline="",
            ) as handle:
                writer = csv.DictWriter(handle, fieldnames=mapping)
                writer.writeheader()
                writer.writerow(mapping)

            before = helper.metadata_request(base, "/api/dashboard")["data"]
            assert before["counts"]["public_preview_papers"] == 1
            assert before["counts"]["map_markers"] == 1
            assert before["counts"]["curated_mappings"] == 1
            assert before["git_status"]["success"]
            assert not before["git_status"]["timed_out"]
            assert "papers.csv" in before["git_status"]["stdout_tail"]
            assert before["action_queues"]["publication_venues"]["count"] == 1

            saved = helper.metadata_request(base, "/api/paper/metadata/update", {
                "id": before["papers"][0]["display_id"], **metadata_tests.chi_venue_fields(),
                "venue_selection_confirmed": True,
            })
            assert saved["success"]
            after = helper.metadata_request(base, "/api/dashboard")["data"]
            assert after["action_queues"]["publication_venues"]["records"] == []
            metric = next(
                item for item in after["action_required"]
                if item["queue"] == "publication_venues"
            )
            assert metric["value"] == 0
            with path.open(encoding="utf-8", newline="") as handle:
                assert next(csv.DictReader(handle))["venue_id"] == "venue:chi"

        assert len(git_calls) == 2
