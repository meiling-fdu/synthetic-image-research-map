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
    ensure_author_mapping_report,
    load_author_mapping_coverage,
    make_handler,
)
from scripts.admin_workflows import ALLOWED_WORKFLOWS
from scripts.admin_review_queues import (
    overall_project_health,
    project_health_data,
    project_health_severity,
)


FIELDS = (
    "priority_rank",
    "mapping_status",
    "priority",
    "triage_status",
    "suggested_action",
    "public_impact",
    "current_mapping_state",
    "known_canonical_institutions",
    "existing_mapping_authors",
    "suggested_author_matches",
    "raw_affiliation_evidence",
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
                "priority": "normal",
                "triage_status": "likely_auto_fixable",
                "suggested_action": "Review existing mapping author names",
                "public_impact": "paper details",
                "current_mapping_state": "confirmed",
                "known_canonical_institutions": "Example University",
                "existing_mapping_authors": "Ada",
                "suggested_author_matches": "Ada L. → Ada",
                "raw_affiliation_evidence": "Example University",
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
                "priority": "high",
                "triage_status": "needs_manual_review",
                "suggested_action": "Find affiliation evidence and add a mapping",
                "public_impact": "paper details; map markers blocked",
                "current_mapping_state": "missing",
                "known_canonical_institutions": "",
                "existing_mapping_authors": "",
                "suggested_author_matches": "",
                "raw_affiliation_evidence": "",
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
                "priority": "",
                "triage_status": "complete",
                "suggested_action": "No mapping action needed",
                "public_impact": "none",
                "current_mapping_state": "confirmed",
                "known_canonical_institutions": "Complete Institute",
                "existing_mapping_authors": "Complete Author",
                "suggested_author_matches": "",
                "raw_affiliation_evidence": "",
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
    def server(self, report_path, generator=None):
        generator = generator or (lambda: {"success": False})
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            make_handler(
                "test-token",
                author_mapping_report_path=report_path,
                author_mapping_report_generator=generator,
            ),
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
        self.assertEqual(
            report["records"][1]["known_canonical_institutions"],
            "Example University",
        )

    def test_loader_missing_report_explains_refresh_action(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.csv"
            with self.assertRaisesRegex(AdminDataError, "Run the refresh pipeline"):
                load_author_mapping_coverage(path)

    def test_startup_generates_only_when_report_is_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.csv"
            calls = []

            def generate():
                calls.append("generated")
                self.write_report(path)
                return {"success": True}

            first = ensure_author_mapping_report(path, generate)
            second = ensure_author_mapping_report(path, generate)

        self.assertTrue(first["generated"])
        self.assertFalse(second["generated"])
        self.assertEqual(calls, ["generated"])

    def test_admin_full_refresh_includes_author_mapping_report(self):
        commands = [" ".join(command) for command in ALLOWED_WORKFLOWS["full_refresh"]]
        self.assertIn(
            "python3 scripts/report_missing_author_mappings.py",
            commands,
        )

    def test_endpoint_returns_report_and_requires_header_token(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.csv"
            self.write_report(path)
            with self.server(path) as base_url:
                status, payload = self.request(
                    f"{base_url}/api/review/author-mapping-coverage"
                )
                unauthorized_status, _ = self.request(
                    f"{base_url}/api/review/author-mapping-coverage",
                    token="wrong",
                )
                alias_status, _ = self.request(
                    f"{base_url}/api/reports/author-mapping-coverage"
                )

        self.assertEqual(status, 200)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["data"]["summary"]["total_public_papers"], 3)
        self.assertEqual(unauthorized_status, 401)
        self.assertEqual(alias_status, 200)

    def test_project_health_uses_author_mapping_report_numbers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.csv"
            self.write_report(path)
            with self.server(path) as base_url:
                status, payload = self.request(f"{base_url}/api/dashboard")

        self.assertEqual(status, 200)
        groups = {
            group["key"]: group
            for group in payload["data"]["project_health"]["groups"]
        }
        mapping_metrics = {
            metric["key"]: metric
            for metric in groups["author_mapping"]["metrics"]
        }
        self.assertEqual(mapping_metrics["author_mapping_coverage"]["value"], 33.3)
        self.assertEqual(mapping_metrics["complete_author_mappings"]["value"], 1)
        self.assertEqual(mapping_metrics["partial_author_mappings"]["value"], 1)
        self.assertEqual(mapping_metrics["missing_author_mappings"]["value"], 1)
        self.assertEqual(mapping_metrics["missing_author_links"]["value"], 4)

    def test_project_health_missing_reports_have_graceful_fallback(self):
        queues = {
            name: {"available": False, "count": 0}
            for name in (
                "high_risk_marker",
                "marker_blocker",
                "key_paper_coverage",
                "manual_import",
            )
        }
        health = project_health_data(
            counts={},
            queues=queues,
            author_mapping_coverage={"available": False, "summary": {}},
        )

        metrics = [
            metric
            for group in health["groups"]
            for metric in group["metrics"]
            if not metric["available"]
        ]
        self.assertTrue(metrics)
        self.assertTrue(
            all(metric["display_value"] == "Report missing" for metric in metrics)
        )
        self.assertNotIn("not found", json.dumps(health).casefold())
        self.assertFalse(health["overall"]["available"])
        self.assertEqual(health["overall"]["display_value"], "Needs refresh")

    def test_project_health_severity_boundaries(self):
        self.assertEqual(
            project_health_severity("author_mapping_coverage", 95), "good"
        )
        self.assertEqual(
            project_health_severity("author_mapping_coverage", 90), "warning"
        )
        self.assertEqual(
            project_health_severity("author_mapping_coverage", 89.9), "critical"
        )
        for key, warning_max in (
            ("missing_author_mappings", 10),
            ("missing_author_links", 50),
            ("missing_coordinates", 5),
            ("missing_affiliations", 20),
        ):
            self.assertEqual(project_health_severity(key, 0), "good")
            self.assertEqual(
                project_health_severity(key, warning_max), "warning"
            )
            self.assertEqual(
                project_health_severity(key, warning_max + 1), "critical"
            )
        self.assertEqual(project_health_severity("marker_blockers", 100), "warning")
        self.assertEqual(project_health_severity("marker_blockers", 101), "critical")

    def test_project_health_score_boundaries_and_caps(self):
        def score(
            *,
            coverage=100,
            coordinates=0,
            affiliations=0,
            high_risk=0,
            blockers=0,
            missing_links=0,
        ):
            return overall_project_health(
                counts={
                    "papers_missing_coordinates": coordinates,
                    "papers_missing_affiliations": affiliations,
                },
                queues={
                    "high_risk_marker": {
                        "available": True,
                        "count": high_risk,
                    },
                    "marker_blocker": {
                        "available": True,
                        "count": blockers,
                    },
                },
                author_mapping_coverage={
                    "available": True,
                    "summary": {
                        "mapping_coverage_percentage": coverage,
                        "total_missing_author_links": missing_links,
                    },
                },
            )

        self.assertEqual(score()["score"], 100)
        self.assertEqual(score()["level"], "Excellent")
        self.assertEqual(score(high_risk=1500)["score"], 90)
        self.assertEqual(score(high_risk=1650)["level"], "Needs attention")
        self.assertEqual(
            score(coverage=0, coordinates=2)["level"],
            "Critical maintenance",
        )
        capped = score(
            coverage=-100,
            coordinates=1000,
            affiliations=1000,
            high_risk=10000,
            blockers=10000,
            missing_links=10000,
        )
        self.assertGreaterEqual(capped["score"], 0)
        self.assertLessEqual(capped["score"], 100)
        self.assertEqual(capped["deductions"]["author_mapping_coverage"], 25)
        self.assertEqual(capped["deductions"]["review_backlog"], 20)

    def test_project_health_includes_existing_queue_breakdowns(self):
        queues = {
            "high_risk_marker": {
                "available": True,
                "count": 614,
                "summary": {"P1": 437, "P2": 177},
            },
            "marker_blocker": {
                "available": True,
                "count": 281,
                "summary": {
                    "already_mapped": 264,
                    "missing_affiliation_rows": 6,
                    "has_affiliation_missing_coordinates": 3,
                },
            },
            "key_paper_coverage": {
                "available": True,
                "count": 298,
                "summary": {
                    "covered_as_map_marker": 121,
                    "missing_from_candidate_pool": 160,
                },
            },
            "manual_import": {
                "available": True,
                "count": 475,
                "summary": {"ready": 207, "manual_review": 111, "weak_match": 85},
            },
        }
        health = project_health_data(
            counts={},
            queues=queues,
            author_mapping_coverage={
                "available": True,
                "summary": {
                    "mapping_coverage_percentage": 100,
                    "total_missing_author_links": 0,
                },
            },
        )
        review_group = next(
            group for group in health["groups"] if group["key"] == "review_queues"
        )
        metrics = {metric["key"]: metric for metric in review_group["metrics"]}
        self.assertEqual(metrics["high_risk_markers"]["display_value"], "614 total")
        self.assertEqual(
            metrics["high_risk_markers"]["detail"],
            "P1: 437 · P2: 177",
        )
        self.assertIn(
            "missing_from_candidate_pool: 160",
            metrics["key_paper_coverage_queue"]["full_detail"],
        )

    def test_project_health_exposes_all_frontend_groups(self):
        queues = {
            name: {"available": True, "count": 0}
            for name in (
                "high_risk_marker",
                "marker_blocker",
                "key_paper_coverage",
                "manual_import",
            )
        }
        health = project_health_data(
            counts={},
            queues=queues,
            author_mapping_coverage={"available": True, "summary": {}},
        )
        self.assertEqual(
            [group["key"] for group in health["groups"]],
            [
                "corpus",
                "author_mapping",
                "institution_location",
                "review_queues",
                "publication_exclusions",
            ],
        )
        repository_root = Path(__file__).resolve().parent.parent
        html = (repository_root / "web" / "admin.html").read_text(encoding="utf-8")
        javascript = (repository_root / "web" / "admin.js").read_text(
            encoding="utf-8"
        )
        self.assertIn('id="project-health-groups"', html)
        self.assertNotIn('id="summary-grid"', html)
        self.assertIn('class="secondary-summary" open', html)
        self.assertIn("function renderProjectHealth()", javascript)
        self.assertIn("navigateConsole(metric.target)", javascript)
        self.assertIn('id="mapping-coverage-triage"', html)
        self.assertIn("row.raw_affiliation_evidence", javascript)

    def test_missing_report_returns_empty_state_and_generate_populates_it(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.csv"
            generated = []

            def generate():
                generated.append(True)
                self.write_report(path)
                return {"success": True}

            with self.server(path, generate) as base_url:
                get_status, get_payload = self.request(
                    f"{base_url}/api/review/author-mapping-coverage"
                )
                dashboard_status, dashboard_payload = self.request(
                    f"{base_url}/api/dashboard"
                )
                generate_status, generate_payload = self.request(
                    f"{base_url}/api/review/author-mapping-coverage/generate",
                    method="POST",
                )

        self.assertEqual(get_status, 200)
        self.assertFalse(get_payload["data"]["available"])
        self.assertEqual(
            get_payload["data"]["message"],
            "Author mapping report has not been generated.",
        )
        self.assertEqual(dashboard_status, 200)
        mapping_group = next(
            group
            for group in dashboard_payload["data"]["project_health"]["groups"]
            if group["key"] == "author_mapping"
        )
        self.assertTrue(
            all(
                metric["display_value"] == "Report missing"
                for metric in mapping_group["metrics"]
            )
        )
        self.assertEqual(generate_status, 200)
        self.assertTrue(generate_payload["data"]["available"])
        self.assertEqual(generated, [True])


if __name__ == "__main__":
    unittest.main()
