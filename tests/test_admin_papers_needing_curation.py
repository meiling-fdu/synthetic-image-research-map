"""Curation is effective paper metadata, independent of diagnostic queues."""
import contextlib
import json
import tempfile
import threading
import unittest
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from scripts import serve_admin as admin
from scripts.admin_review_queues import ACTION_QUEUES
from tests.test_paper_metadata_editing import curated_row, write_papers, write_exclusions, chi_venue_fields


class PapersNeedingCurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.papers = self.root / "papers.csv"
        self.exclusions = self.root / "exclusions.csv"
        self.public = self.root / "public.json"
        self.empty = self.root / "empty.json"
        self.empty.write_text("[]")
        (self.root / "mappings.csv").write_text("paper_id,mapping_status\n")
        self.rows = [curated_row(
            paper_id=f"curated:{name}", title=name, doi=f"10.1000/{name}",
            **chi_venue_fields(), curation_status="needs_review",
            review_status="reviewed",
        ) for name in ("Reopened", "Excluded", "Superseded", "Confirmed", "Outside")]
        self.rows[3]["curation_status"] = "confirmed"
        self.rows[4]["scope_status"] = "out_of_scope"
        write_papers(self.papers, self.rows)
        write_exclusions(self.exclusions, [{"paper_id": "curated:Excluded", "doi": "10.1000/Excluded", "is_active": "true"}])
        # Deliberately stale public statuses, and a duplicate of one source row.
        exported = [dict(row, notes="Check the original source", curation_status="confirmed" if index == 0 else "needs_review")
                    for index, row in enumerate(self.rows)]
        self.public.write_text(json.dumps([*exported, exported[0],
            {"paper_id": "public:unreviewed", "title": "Imported without status", "year": 2026},
            {"paper_id": "public:inactive", "title": "Inactive", "curation_status": "needs_review", "is_active": False},
            {"paper_id": "public:superseded", "title": "Retired", "curation_status": "needs_review", "paper_status": "superseded"},
        ]))
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        for name, value in (("PUBLIC_PAPERS_PATH", self.public), ("PUBLIC_MAP_PATH", self.empty)):
            self.stack.enter_context(patch.object(admin, name, value))
        self.stack.enter_context(patch.object(admin, "read_paper_version_merges", return_value=[{
            "duplicate_doi": "10.1000/Superseded", "status": "confirmed_duplicate", "is_active": "true",
        }]))

    def load(self):
        return admin.load_admin_data(self.exclusions, self.papers,
                                     self.root / "mappings.csv", self.empty)

    def test_effective_status_lifecycle_and_deduplication(self):
        papers, data = self.load()
        needs = admin.filtered_curation_papers(papers, "needs_review")
        self.assertEqual([r["title"] for r in needs], ["Imported without status", "Reopened"])
        self.assertEqual(len(papers), len(data["papers_by_id"]))
        self.assertEqual(sum(r["title"] == "Reopened" for r in papers), 1)
        reopened = needs[1]
        self.assertEqual(reopened["review_status"], "reviewed")
        self.assertEqual(reopened["notes"], "Check the original source")
        summary = admin.paper_summary(reopened)
        for field in ("curation_status", "review_status", "scope_status", "is_active_corpus", "notes"):
            self.assertEqual(summary[field], reopened[field])

    def test_curated_activity_overrides_stale_public_activity(self):
        # Activity fields are optional today; honor them whenever modeled.
        original_read = admin.read_csv_rows
        def read(path):
            rows = original_read(path)
            if path == self.papers:
                rows[0]["is_active"] = "false"
            return rows
        with patch.object(admin, "read_csv_rows", side_effect=read):
            self.assertEqual([p["title"] for p in admin.filtered_curation_papers(self.load()[0], "needs_review")],
                             ["Imported without status"])

    @contextlib.contextmanager
    def server(self):
        with contextlib.ExitStack() as stack:
            # Keep ancillary diagnostic/report work outside this curation test.
            stack.enter_context(patch.object(admin, "build_action_queues", return_value={
                name: {"count": 0, "available": True, "records": [], "summary": {}}
                for name in ACTION_QUEUES
            }))
            stack.enter_context(patch.object(admin, "location_review_payload", return_value={
                "records": [], "summary": {"needs_coordinates": 0}, "total_unresolved": 0,
            }))
            stack.enter_context(patch.object(admin, "load_author_mapping_coverage", return_value={}))
            stack.enter_context(patch.object(admin, "git_status_result", return_value={}))
            handler = admin.make_handler(
                "curation-test-token", curated_papers_path=self.papers, exclusions_path=self.exclusions,
                curated_arxiv_links_path=self.root / "arxiv.csv",
                public_preview_sync_state_path=self.root / "sync.json",
                metadata_export_runner=lambda _: {"success": True, "exit_code": 0},
            )
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                yield f"http://127.0.0.1:{server.server_port}"
            finally:
                server.shutdown()
                server.server_close()
                worker.join()

    def request(self, base, path, payload=None):
        request = urllib.request.Request(base + path,
            data=None if payload is None else json.dumps(payload).encode(),
            headers={"X-Admin-Token": "curation-test-token", "Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=30) as response:
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            return json.load(response)

    def assert_snapshot(self, base, count):
        dashboard = self.request(base, "/api/dashboard")["data"]
        full = self.request(base, "/api/papers?curation_status=needs_review")
        self.assertEqual(dashboard["papers_needing_curation"], full)
        self.assertEqual(full["count"], count)
        self.assertEqual(len({r["display_id"] for r in full["records"]}), count)
        self.assertEqual(admin.filtered_curation_papers(dashboard["papers"], "needs_review"), full["records"])
        return full

    def test_http_dashboard_list_editor_and_save_refresh_both_directions(self):
        with self.server() as base:
            full = self.assert_snapshot(base, 2)
            paper = next(r for r in full["records"] if r["title"] == "Reopened")
            query = urllib.parse.urlencode({"id": paper["display_id"]})
            detail = self.request(base, "/api/paper?" + query)["paper"]
            editor = self.request(base, "/api/paper/metadata?" + query)["data"]["effective_record"]
            self.assertEqual(detail["title"], paper["title"])
            self.assertEqual(editor["curation_status"], paper["curation_status"])
            for status, count in (("confirmed", 1), ("needs_review", 2)):
                saved = self.request(base, "/api/paper/metadata/update", {
                    "id": paper["display_id"], "curation_status": status,
                })
                self.assertTrue(saved["saved"])
                self.assertEqual(saved["data"]["paper"]["curation_status"], status)
                self.assert_snapshot(base, count)
            # Neither save regenerated the deliberately stale fixture export.
            self.assertEqual(json.loads(self.public.read_text())[0]["curation_status"], "confirmed")

    def test_frontend_sends_explicit_curation_choice(self):
        source = (admin.REPOSITORY_ROOT / "web/admin.js").read_text()
        save = source.split("async function saveMetadata(event)", 1)[1].split("function renderPaperDetail", 1)[0]
        self.assertIn('draft.curation_status = elements["metadata-curation-status"].value;', save)
        self.assertNotIn('draft.curation_status = "confirmed"', save)


if __name__ == "__main__":
    unittest.main()
