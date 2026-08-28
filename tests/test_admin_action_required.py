"""Action Required is a projection of effective queues, never diagnostic totals."""
import contextlib
import csv
import json
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from scripts import admin_review_queues as queues
from scripts.serve_admin import make_handler
from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS, INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_COLUMNS, INSTITUTION_LOCATION_REVIEW_COLUMNS,
    INSTITUTION_ALIAS_COLUMNS,
)
from scripts.curated_locations import location_review_payload


def write_rows(path, rows):
    fields = (AUTHOR_INSTITUTION_MAPPING_COLUMNS if path.name == "mappings.csv" else
              list(dict.fromkeys(key for row in rows for key in row)) or ["title"])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


class ActionRequiredTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=queues.REPOSITORY_ROOT)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.paths = {}
        for name in ("mappings", "exclusions", "papers", "institutions", "decisions",
                     "record_overrides", "author_overrides", "corrections"):
            self.paths[name + "_path"] = self.root / (name + ".csv")
            write_rows(self.paths[name + "_path"], [])
        for name in ("public_papers", "public_map"):
            self.paths[name + "_path"] = self.root / (name + ".json")
            self.paths[name + "_path"].write_text("[]")
        self.base = {"title": "Unresolved paper", "year": "2026", "doi": "10.test/paper"}

    def context(self):
        return queues.ReviewContext(**self.paths, merge_rows=[])

    def candidate(self, name, **kwargs):
        row = dict(self.base, review_type="needs_review", **kwargs)
        if name in {"high_risk_marker", "missing_coordinates"}:
            row.update(institution="Example University", institution_id="institution:one")
        return row

    def test_all_categories_terminal_suppression_and_deduplication(self):
        for name in queues.ACTION_QUEUES:
            for status in queues.TERMINAL_STATUSES:
                with self.subTest(queue=name, status=status):
                    q = queues.actionable_payload(name, [self.candidate(name, review_status=status)], self.context())
                    self.assertEqual(q["records"], [])
                    self.assertEqual(q["count"], 0)
            row = self.candidate(name)
            q = queues.actionable_payload(name, [row, dict(row, source_file="historical.csv")], self.context())
            self.assertEqual(q["count"], 1, name)
            self.assertEqual(len(q["records"]), q["total_unresolved"])
            self.assertEqual(q["suppression_reasons"]["duplicate_diagnostic"], 1)

    def test_all_categories_exclusions_inactive_papers_and_decision_precedence(self):
        for name in queues.ACTION_QUEUES:
            row = self.candidate(name)
            with self.subTest(queue=name):
                write_rows(self.paths["exclusions_path"], [dict(self.base, is_active="true")])
                self.assertEqual(queues.actionable_payload(name, [row], self.context())["count"], 0)
                write_rows(self.paths["exclusions_path"], [])
                write_rows(self.paths["papers_path"], [dict(self.base, paper_status="inactive")])
                self.assertEqual(queues.actionable_payload(name, [row], self.context())["count"], 0)
                write_rows(self.paths["papers_path"], [])
                decision = dict(row, review_queue=name, action="no_action_after_review", updated_at="2026-08-28")
                write_rows(self.paths["decisions_path"], [decision])
                self.assertEqual(queues.actionable_payload(name, [row], self.context())["count"], 0)
                # A new explicit unresolved decision beats a stale generated resolution.
                write_rows(self.paths["decisions_path"], [dict(decision, action="unresolved")])
                self.assertEqual(queues.actionable_payload(name, [dict(row, review_status="resolved")], self.context())["count"], 1)
                write_rows(self.paths["decisions_path"], [])

    def test_inactive_institutions_and_curated_marker_overrides(self):
        for name in ("high_risk_marker", "missing_coordinates"):
            row = self.candidate(name)
            write_rows(self.paths["institutions_path"], [{"institution_id": "institution:one", "institution_status": "inactive"}])
            self.assertEqual(queues.actionable_payload(name, [row], self.context())["count"], 0)
        write_rows(self.paths["institutions_path"], [])
        row = self.candidate("high_risk_marker")
        write_rows(self.paths["mappings_path"], [dict(row, mapping_status="active")])
        self.assertEqual(queues.actionable_payload("high_risk_marker", [row], self.context())["count"], 0)
        write_rows(self.paths["mappings_path"], [dict(row, mapping_status="excluded")])
        self.assertEqual(queues.actionable_payload("high_risk_marker", [row], self.context())["count"], 0)

    def test_current_import_and_title_only_coverage_resolution(self):
        write_rows(self.paths["papers_path"], [dict(self.base, paper_id="curated:one", review_status="reviewed")])
        title_only = {"title": self.base["title"], "year": "2026"}
        self.assertEqual(queues.actionable_payload("manual_import", [title_only], self.context())["count"], 0)
        self.paths["public_map_path"].write_text(json.dumps([self.base]))
        self.assertEqual(queues.actionable_payload("key_paper_coverage", [title_only], self.context())["count"], 0)
        # A metadata confirmation does not resolve an unrelated marker.
        self.assertEqual(queues.actionable_payload("high_risk_marker", [self.candidate("high_risk_marker")], self.context())["count"], 1)

    def test_historical_no_action_rows_do_not_enter_action_required(self):
        for name, row in (
            ("marker_blocker", dict(self.base, blocker_type="already_mapped")),
            ("key_paper_coverage", dict(self.base, missing_stage="covered_as_map_marker")),
            ("manual_import", dict(self.base, recommended_action="no_action")),
        ):
            q = queues.actionable_payload(name, [row], self.context())
            self.assertEqual(q["raw_count"], 1)
            self.assertEqual(q["count"], 0)

    def test_identifier_variants_deduplicate_without_fuzzy_paper_merging(self):
        rows = [dict(self.base, openalex_url="https://openalex.org/W1"),
                {"openalex_id": "W1", "title": self.base["title"], "year": "2026"},
                {"title": self.base["title"], "year": "2026"}]
        q = queues.actionable_payload("manual_import", rows, self.context())
        self.assertEqual(q["count"], 1)
        self.assertEqual(len(q["records"][0]["diagnostic_sources"]), 3)
        rows.append(dict(self.base, doi="10.test/different"))
        q = queues.actionable_payload("manual_import", rows, self.context())
        self.assertEqual(q["count"], 3)  # two distinct DOI records + uncertain title-only record

    def test_real_location_queue_effective_status_and_scope(self):
        def write_schema(path, columns, rows):
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(rows)
        reviews = self.root / "locations_review.csv"
        locations = self.root / "locations.csv"
        aliases = self.root / "aliases.csv"
        institution = {"institution_id": "institution:one", "canonical_name": "Example University",
                       "institution_type": "university", "institution_status": "active"}
        write_schema(self.paths["institutions_path"], INSTITUTION_COLUMNS, [institution])
        row = dict(self.candidate("missing_coordinates"), review_status="pending_review",
                   coordinate_status="missing", location_status="missing")
        write_schema(reviews, INSTITUTION_LOCATION_REVIEW_COLUMNS, [row, row])
        write_schema(locations, INSTITUTION_LOCATION_COLUMNS, [])
        write_schema(aliases, INSTITUTION_ALIAS_COLUMNS, [])
        # Confirmed author evidence does not resolve missing coordinates.
        write_rows(self.paths["mappings_path"], [dict(row, mapping_status="active")])

        def payload():
            context = self.context()
            result = location_review_payload(
                review_path=reviews, locations_path=locations, aliases_path=aliases,
                institutions_path=self.paths["institutions_path"],
                mappings=context.rows["mappings"], exclusions=context.rows["exclusions"],
                paper_is_suppressed=context.paper_suppression)
            q = queues.build_action_queues(context, location_payload=result,
                                           author_mapping_coverage={}, papers=[])["missing_coordinates"]
            return result, q
        result, q = payload()
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(q["count"], 1)
        write_schema(locations, INSTITUTION_LOCATION_COLUMNS, [dict(
            institution, institution="Example University", location_id="location:one",
            lat="45", lon="9", location_status="confirmed", coordinate_status="known")])
        result, q = payload()
        self.assertEqual(result["records"][0]["effective_review_status"], "confirmed")
        self.assertEqual(q["count"], 0)
        write_schema(locations, INSTITUTION_LOCATION_COLUMNS, [])
        write_schema(self.paths["institutions_path"], INSTITUTION_COLUMNS,
                     [dict(institution, institution_status="ignored")])
        self.assertEqual(payload()[1]["count"], 0)
        write_schema(self.paths["institutions_path"], INSTITUTION_COLUMNS, [institution])
        write_rows(self.paths["papers_path"], [dict(self.base, paper_status="inactive")])
        self.assertEqual(payload()[1]["count"], 0)

    @contextlib.contextmanager
    def server(self):
        diagnostic_paths = {}
        for name in queues.QUEUE_PATHS:
            diagnostic_paths[name] = self.root / (name + ".csv")
            candidates = [self.candidate(name)]
            if name == "high_risk_marker":
                candidates.append(self.candidate("high_risk_paper"))
            write_rows(diagnostic_paths[name], candidates * 2)
        imports = self.root / "key_papers_test_manual_review.csv"
        write_rows(imports, [self.base, self.base])
        counts = {"total_papers": 1, "curated_papers": 0, "active_exclusions": 0,
                  "papers_missing_affiliations": 1}
        location = dict(self.candidate("missing_coordinates"), actionable=True,
                        review_status="pending_review", has_usable_confirmed_location=False)
        location_payload = {"records": [location], "summary": {"needs_coordinates": 1}, "total_unresolved": 1}
        coverage = {"records": [dict(self.base, mapping_status="zero")], "summary": {"zero_mappings": 1}, "available": True}
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.dict(queues.QUEUE_PATHS, diagnostic_paths))
            stack.enter_context(patch.object(queues, "_manual_import_files", return_value=[imports]))
            # Only non-queue report producers are stubbed. Real loaders, effective
            # resolver, configured paths, dashboard, and HTTP routes execute.
            stack.enter_context(patch("scripts.serve_admin.load_admin_data", return_value=([dict(self.base, missing_affiliation=True)], {"status": {"counts": counts}})))
            stack.enter_context(patch("scripts.serve_admin.location_review_payload", return_value=location_payload))
            stack.enter_context(patch("scripts.serve_admin.load_author_mapping_coverage", return_value=coverage))
            stack.enter_context(patch("scripts.serve_admin.git_status_result", return_value={}))
            handler = make_handler("test-action-token", mappings_path=self.paths["mappings_path"],
                                   exclusions_path=self.paths["exclusions_path"],
                                   curated_papers_path=self.paths["papers_path"],
                                   institutions_path=self.paths["institutions_path"],
                                   review_decisions_path=self.paths["decisions_path"])
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                yield f"http://127.0.0.1:{server.server_port}"
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

    def get(self, base, endpoint):
        request = urllib.request.Request(base + endpoint, headers={"X-Admin-Token": "test-action-token"})
        with urllib.request.urlopen(request, timeout=30) as response:
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            return json.load(response)["data"]

    def assert_snapshot(self, base, expected):
        snapshot = self.get(base, "/api/dashboard")
        self.assertEqual(len(snapshot["action_required"]), len(queues.ACTION_QUEUES))
        for metric in snapshot["action_required"]:
            name = metric["queue"]
            detail = self.get(base, metric["endpoint"])
            with self.subTest(queue=name):
                self.assertEqual(metric["target"], queues.ACTION_QUEUES[name][2])
                self.assertEqual(metric["value"], detail["count"])
                self.assertEqual(metric["value"], len(detail["records"]))
                self.assertEqual(detail["records"], snapshot["action_queues"][name]["records"])
                self.assertEqual(len({r["actionable_id"] for r in detail["records"]}), detail["count"])
                # This fixture supplies marker findings, not venue metadata.
                self.assertEqual(detail["count"], 0 if name == "publication_venues" else expected)
                if metric["value"]:
                    self.assertTrue(detail["records"], "Non-zero summary must never open an empty unfiltered queue")
        return snapshot

    def test_http_summary_detail_invariant_and_refresh_after_curated_changes(self):
        with self.server() as base:
            self.assert_snapshot(base, 1)
            # Reports stay unchanged: Refresh must pick up the durable override.
            write_rows(self.paths["exclusions_path"], [dict(self.base, is_active="true")])
            self.assert_snapshot(base, 0)
            write_rows(self.paths["exclusions_path"], [])
            self.assert_snapshot(base, 1)


if __name__ == "__main__":
    unittest.main()
