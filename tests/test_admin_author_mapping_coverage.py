import csv
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from contextlib import contextmanager
from http.server import ThreadingHTTPServer
from pathlib import Path

from scripts.serve_admin import (
    AdminDataError,
    load_author_mapping_coverage,
    make_handler,
)


FIELDS = (
    "priority_rank",
    "mapping_status",
    "paper_id",
    "title",
    "year",
    "venue",
    "is_key_paper",
    "is_curated_paper",
    "total_authors",
    "mapped_authors",
    "missing_authors",
    "missing_author_names",
    "marker_count",
    "doi",
    "arxiv_id",
    "openalex_id",
    "url",
)


class AdminAuthorMappingCoverageTests(unittest.TestCase):
    def write_report(self, path):
        rows = [
            {
                "priority_rank": 2,
                "mapping_status": "partial",
                "title": "Partial",
                "year": 2024,
                "is_key_paper": "false",
                "is_curated_paper": "true",
                "total_authors": 3,
                "mapped_authors": 1,
                "missing_authors": 2,
                "missing_author_names": "Ada; Ben",
                "marker_count": 1,
            },
            {
                "priority_rank": 1,
                "mapping_status": "zero",
                "title": "Zero",
                "year": 2025,
                "is_key_paper": "true",
                "is_curated_paper": "false",
                "total_authors": 2,
                "mapped_authors": 0,
                "missing_authors": 2,
                "missing_author_names": "Cora; Dino",
                "marker_count": 0,
            },
            {
                "priority_rank": 3,
                "mapping_status": "complete",
                "title": "Complete",
                "year": 2023,
                "is_key_paper": "false",
                "is_curated_paper": "false",
                "total_authors": 2,
                "mapped_authors": 2,
                "missing_authors": 0,
                "missing_author_names": "",
                "marker_count": 3,
            },
        ]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    @contextmanager
    def server(self, report_path):
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            make_handler("test-token", author_mapping_report_path=report_path),
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def request(self, url, method="GET", token="test-token"):
        request = urllib.request.Request(
            url,
            method=method,
            headers={"X-Admin-Token": token},
            data=b"{}" if method == "POST" else None,
        )
        try:
            with urllib.request.urlopen(request) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    def test_loader_summarizes_and_sorts_report(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.csv"
            self.write_report(path)

            report = load_author_mapping_coverage(path)

        self.assertEqual(
            [row["title"] for row in report["records"]],
            ["Zero", "Partial", "Complete"],
        )
        self.assertEqual(
            report["summary"],
            {
                "total_public_papers": 3,
                "complete_mappings": 1,
                "partial_mappings": 1,
                "zero_mappings": 1,
                "total_missing_author_links": 4,
                "mapping_coverage_percentage": 33.3,
                "map_markers_reconciled": 4,
            },
        )
        self.assertTrue(report["records"][0]["is_key_paper"])

    def test_loader_missing_report_explains_refresh_action(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.csv"
            with self.assertRaisesRegex(AdminDataError, "Run the refresh pipeline"):
                load_author_mapping_coverage(path)

    def test_endpoint_returns_report_and_requires_header_token(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.csv"
            self.write_report(path)
            with self.server(path) as base_url:
                status, payload = self.request(
                    f"{base_url}/api/reports/author-mapping-coverage"
                )
                unauthorized_status, _ = self.request(
                    f"{base_url}/api/reports/author-mapping-coverage",
                    token="wrong",
                )

        self.assertEqual(status, 200)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["summary"]["total_public_papers"], 3)
        self.assertEqual(unauthorized_status, 401)

    def test_endpoint_is_read_only_and_missing_report_is_graceful(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.csv"
            with self.server(path) as base_url:
                get_status, get_payload = self.request(
                    f"{base_url}/api/reports/author-mapping-coverage"
                )
                post_status, _ = self.request(
                    f"{base_url}/api/reports/author-mapping-coverage",
                    method="POST",
                )

        self.assertEqual(get_status, 404)
        self.assertIn("Run the refresh pipeline", get_payload["errors"][0])
        self.assertEqual(post_status, 405)


if __name__ == "__main__":
    unittest.main()
