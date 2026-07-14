import csv
import contextlib
import json
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from io import BytesIO
from email.message import Message
from pathlib import Path

from scripts.arxiv_autofill import (
    ArxivLookupError,
    autofill_missing_arxiv_ids,
    autofill_public_map_arxiv_ids,
    eligible_public_map_papers,
    lookup_arxiv_by_title,
    normalize_exact_title,
)
from scripts.curated_export import integrate_curated_records
from scripts.curated_schema import PAPERS_COLUMNS
from scripts.curated_schema import PAPER_EXCLUSION_COLUMNS
from scripts.export_candidate_map_data import apply_paper_arxiv_links
from scripts.serve_admin import (
    ARXIV_AUTOFILL_STATE,
    ARXIV_AUTOFILL_STATE_LOCK,
    make_handler,
)
from http.server import ThreadingHTTPServer


def paper(**overrides):
    row = {column: "" for column in PAPERS_COLUMNS}
    row.update({
        "paper_id": "curated:one",
        "title": "Detecting Synthetic Images: A Survey",
        "year": "2025",
        "authors": "Alice Example; Bob Example",
        "task": "detection",
        "entry_type": "survey",
        "scope_status": "in_scope",
        "source_database": "manual",
        "review_status": "reviewed",
    })
    row.update(overrides)
    return row


def write_rows(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAPERS_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


ATOM_SUCCESS = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry><id>https://arxiv.org/abs/2501.01234v2</id>
  <title>Detecting Synthetic Images: A Survey</title></entry>
</feed>"""


class Response:
    def __init__(self, payload=ATOM_SUCCESS):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.payload


class TimeoutRecordingResponse(Response):
    class Socket:
        def __init__(self):
            self.timeout = None

        def settimeout(self, value):
            self.timeout = value

    def __init__(self, payload=ATOM_SUCCESS):
        super().__init__(payload)
        self.socket = self.Socket()
        self.fp = type("FP", (), {
            "raw": type("Raw", (), {"_sock": self.socket})()
        })()


def http_error(status, retry_after=None):
    headers = Message()
    if retry_after is not None:
        headers["Retry-After"] = str(retry_after)
    return urllib.error.HTTPError(
        "https://export.arxiv.org/api/query", status, "test error", headers, BytesIO()
    )


def map_record(title, openalex_id, **overrides):
    record = {
        "id": f"marker:{openalex_id}",
        "title": title,
        "year": 2025,
        "publication_year": 2025,
        "openalex_url": f"https://openalex.org/{openalex_id}",
        "arxiv_id": "",
        "paper_url": "",
        "in_scope": True,
        "task": "detection",
        "subtask": "synthetic_image_detection",
        "entry_type": "method",
        "institution": "Example University",
        "latitude": 43.0,
        "longitude": 11.0,
        "resolution_confidence": "high",
        "needs_review": False,
    }
    record.update(overrides)
    return record


def write_exclusions(path, rows=()):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAPER_EXCLUSION_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


class ArxivAutofillTests(unittest.TestCase):
    def run_batch(self, rows, lookup, export=None):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "papers.csv"
        write_rows(path, rows)
        stats = autofill_missing_arxiv_ids(path=path, lookup=lookup, export=export)
        return stats, read_rows(path)

    def test_unique_exact_match_fills_id_url_and_strips_version(self):
        stats, rows = self.run_batch(
            [paper(paper_url="")],
            lambda _title: [{
                "title": "Detecting Synthetic Images: A Survey",
                "arxiv_id": "2501.01234v2",
            }],
        )
        self.assertEqual(stats["exact_matches_added"], 1)
        self.assertEqual(rows[0]["arxiv_id"], "2501.01234")
        self.assertEqual(rows[0]["paper_url"], "https://arxiv.org/pdf/2501.01234.pdf")
        self.assertEqual(rows[0]["authors"], "Alice Example; Bob Example")
        self.assertNotIn("[object Object]", rows[0]["authors"])
        self.assertNotIn("arxiv_url", rows[0])

    def test_case_entities_unicode_whitespace_quotes_dashes_and_punctuation(self):
        database = "Rock &amp; Roll — ‘Detection’!"
        candidate = "  ROCK & ROLL - 'detection'  "
        self.assertEqual(normalize_exact_title(database), normalize_exact_title(candidate))
        stats, rows = self.run_batch(
            [paper(title=database)],
            lambda _title: [{"title": candidate, "arxiv_id": "cs/9901001v3"}],
        )
        self.assertEqual(stats["exact_matches_added"], 1)
        self.assertEqual(rows[0]["arxiv_id"], "cs/9901001")

    def test_added_removed_changed_words_and_subtitle_differences_do_not_match(self):
        for candidate in (
            "Detecting Synthetic Images: A Comprehensive Survey",
            "Detecting Images: A Survey",
            "Attributing Synthetic Images: A Survey",
            "Detecting Synthetic Images: A Review",
        ):
            with self.subTest(candidate=candidate):
                stats, rows = self.run_batch(
                    [paper()],
                    lambda _title, candidate=candidate: [{"title": candidate, "arxiv_id": "2501.00001"}],
                )
                self.assertEqual(stats["no_match_count"], 1)
                self.assertEqual(rows[0]["arxiv_id"], "")

    def test_zero_and_multiple_matches_are_skipped(self):
        stats, rows = self.run_batch([paper()], lambda _title: [])
        self.assertEqual(stats["no_match_count"], 1)
        self.assertEqual(rows[0]["arxiv_id"], "")
        exact = {"title": paper()["title"], "arxiv_id": "2501.00001"}
        stats, rows = self.run_batch([paper()], lambda _title: [exact, {**exact, "arxiv_id": "2501.00002"}])
        self.assertEqual(stats["ambiguous_match_count"], 1)
        self.assertEqual(rows[0]["arxiv_id"], "")

    def test_existing_id_and_existing_paper_url_are_preserved(self):
        calls = []
        stats, rows = self.run_batch(
            [paper(arxiv_id="1111.22222", paper_url="https://publisher.test/paper")],
            lambda title: calls.append(title),
        )
        self.assertEqual(stats["already_containing_arxiv_ids"], 1)
        self.assertEqual(calls, [])
        self.assertEqual(rows[0]["arxiv_id"], "1111.22222")
        self.assertEqual(rows[0]["paper_url"], "https://publisher.test/paper")

        stats, rows = self.run_batch(
            [paper(paper_url="https://publisher.test/paper")],
            lambda _title: [{"title": paper()["title"], "arxiv_id": "2501.12345"}],
        )
        self.assertEqual(rows[0]["paper_url"], "https://publisher.test/paper")

    def test_failed_lookup_does_not_stop_batch(self):
        def lookup(title):
            if title == "Broken lookup":
                raise TimeoutError("timed out")
            return [{"title": title, "arxiv_id": "2501.12345"}]
        stats, rows = self.run_batch(
            [paper(title="Broken lookup"), paper(paper_id="curated:two", title="Working lookup")],
            lookup,
        )
        self.assertEqual(stats["failed_lookup_count"], 1)
        self.assertEqual(stats["failed_lookups"][0]["title"], "Broken lookup")
        self.assertIn("timed out", stats["failed_lookups"][0]["reason"])
        self.assertEqual(stats["exact_matches_added"], 1)
        self.assertEqual(rows[1]["arxiv_id"], "2501.12345")

    def test_repeated_execution_is_idempotent_and_export_runs_after_update(self):
        export_calls = []
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "papers.csv"
        write_rows(path, [paper()])
        lookup = lambda title: [{"title": title, "arxiv_id": "2501.12345"}]
        first = autofill_missing_arxiv_ids(
            path=path, lookup=lookup,
            export=lambda: export_calls.append("export") or {"success": True},
        )
        second = autofill_missing_arxiv_ids(
            path=path, lookup=lookup,
            export=lambda: export_calls.append("export") or {"success": True},
        )
        self.assertTrue(first["export_ran"])
        self.assertFalse(second["export_ran"])
        self.assertEqual(export_calls, ["export"])
        self.assertEqual(second["already_containing_arxiv_ids"], 1)

    def test_curated_export_propagates_arxiv_id(self):
        exported, _markers, _reviews, _summary = integrate_curated_records(
            [], [], [paper(arxiv_id="cs/9901001")], []
        )
        self.assertEqual(exported[0]["arxiv_id"], "cs/9901001")


class ArxivRequestReliabilityTests(unittest.TestCase):
    def run_lookup(self, outcomes):
        calls = []
        sleeps = []

        def urlopen(_request, timeout):
            calls.append(timeout)
            outcome = outcomes.pop(0)
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome

        result = lookup_arxiv_by_title(
            "Detecting Synthetic Images: A Survey",
            urlopen=urlopen,
            sleep=sleeps.append,
        )
        return result, calls, sleeps

    def test_timeout_followed_by_success(self):
        results, calls, sleeps = self.run_lookup(
            [TimeoutError("socket timed out"), Response()]
        )
        self.assertEqual(results[0]["arxiv_id"], "2501.01234")
        self.assertEqual(len(calls), 2)
        self.assertEqual(sleeps, [3.0])
        self.assertEqual(calls, [10.0, 10.0])

    def test_connection_and_read_timeouts_are_explicit(self):
        response = TimeoutRecordingResponse()
        connection_timeouts = []
        lookup_arxiv_by_title(
            "Detecting Synthetic Images: A Survey",
            urlopen=lambda _request, timeout: connection_timeouts.append(timeout) or response,
            sleep=self.fail,
        )
        self.assertEqual(connection_timeouts, [10.0])
        self.assertEqual(response.socket.timeout, 20.0)

    def test_http_429_followed_by_success(self):
        results, calls, sleeps = self.run_lookup([http_error(429), Response()])
        self.assertEqual(results[0]["arxiv_id"], "2501.01234")
        self.assertEqual(len(calls), 2)
        self.assertEqual(sleeps, [3.0])

    def test_retry_after_header_controls_delay(self):
        _results, _calls, sleeps = self.run_lookup(
            [http_error(429, retry_after="17"), Response()]
        )
        self.assertEqual(sleeps, [17.0])

    def test_failure_after_retry_exhaustion(self):
        outcomes = [TimeoutError("late")] * 3
        sleeps = []
        calls = []

        def urlopen(_request, timeout):
            calls.append(timeout)
            raise outcomes.pop(0)

        with self.assertRaises(ArxivLookupError) as raised:
            lookup_arxiv_by_title("Title", urlopen=urlopen, sleep=sleeps.append)
        self.assertEqual(raised.exception.kind, "timeout")
        self.assertEqual(raised.exception.attempts, 3)
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleeps, [3.0, 8.0])

    def test_permanent_http_400_is_not_retried(self):
        calls = []

        def urlopen(_request, timeout):
            calls.append(timeout)
            raise http_error(400)

        with self.assertRaises(ArxivLookupError) as raised:
            lookup_arxiv_by_title("Title", urlopen=urlopen, sleep=self.fail)
        self.assertEqual(raised.exception.http_status, 400)
        self.assertEqual(raised.exception.attempts, 1)
        self.assertEqual(len(calls), 1)

    def test_valid_zero_result_and_invalid_xml_are_not_retried(self):
        empty_feed = Response(b'<feed xmlns="http://www.w3.org/2005/Atom"/>')
        results, calls, sleeps = self.run_lookup([empty_feed])
        self.assertEqual(results, [])
        self.assertEqual(len(calls), 1)
        self.assertEqual(sleeps, [])

        calls = []
        with self.assertRaises(ArxivLookupError) as raised:
            lookup_arxiv_by_title(
                "Title",
                urlopen=lambda _request, timeout: calls.append(timeout) or Response(b"<broken"),
                sleep=self.fail,
            )
        self.assertEqual(raised.exception.kind, "xml_parsing_error")
        self.assertIn("XML parsing error", raised.exception.reason)
        self.assertEqual(len(calls), 1)

    def test_batch_paces_normal_requests(self):
        sleeps = []
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "papers.csv"
        write_rows(path, [
            paper(title="First"),
            paper(paper_id="curated:two", title="Second"),
        ])
        autofill_missing_arxiv_ids(
            path=path,
            lookup=lambda _title: [],
            request_delay_seconds=2.5,
            sleep=sleeps.append,
        )
        self.assertEqual(sleeps, [2.5])

    def test_batch_continues_after_exhausted_failure(self):
        failure = ArxivLookupError(
            "HTTP 503: unavailable",
            kind="http_error",
            http_status=503,
            attempts=3,
        )

        def lookup(title):
            if title == "Broken lookup":
                raise failure
            return [{"title": title, "arxiv_id": "2501.12345"}]

        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "papers.csv"
        write_rows(path, [
            paper(title="Broken lookup"),
            paper(paper_id="curated:two", title="Working lookup"),
        ])
        stats = autofill_missing_arxiv_ids(path=path, lookup=lookup)
        rows = read_rows(path)
        self.assertEqual(stats["failed_lookup_count"], 1)
        self.assertEqual(stats["failed_lookups"][0]["http_status"], 503)
        self.assertEqual(stats["failed_lookups"][0]["attempts"], 3)
        self.assertEqual(stats["exact_matches_added"], 1)
        self.assertEqual(rows[1]["arxiv_id"], "2501.12345")


class PublicMapAutofillScopeTests(unittest.TestCase):
    def workspace(self, records, exclusions=()):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        map_path = root / "public_map.json"
        map_path.write_text(json.dumps({"records": records}), encoding="utf-8")
        exclusions_path = root / "exclusions.csv"
        write_exclusions(exclusions_path, exclusions)
        return root, map_path, exclusions_path, root / "arxiv_links.csv"

    def test_all_unique_map_papers_are_scanned_once_not_curated_subset(self):
        records = []
        for index in range(130):
            records.append(map_record(f"Paper {index}", f"W{index}"))
        records.append({**records[0], "id": "duplicate-institution", "institution": "Other University"})
        root, map_path, exclusions_path, links_path = self.workspace(records)
        queried = []
        stats = autofill_public_map_arxiv_ids(
            map_path=map_path,
            links_path=links_path,
            exclusions_path=exclusions_path,
            lookup=lambda title: queried.append(title) or [],
        )
        self.assertEqual(stats["total_records"], 130)
        self.assertEqual(stats["eligible_public_map_papers"], 130)
        self.assertEqual(stats["papers_requiring_lookup"], 130)
        self.assertEqual(len(queried), 130)
        self.assertEqual(queried.count("Paper 0"), 1)
        self.assertGreater(stats["total_records"], 124)

    def test_excluded_retracted_review_and_absent_records_are_not_queried(self):
        eligible = map_record("Eligible", "W1")
        excluded = map_record("Excluded", "W2")
        records = [
            eligible,
            excluded,
            map_record("Retracted", "W3", publication_type="retracted"),
            map_record("Review", "W4", needs_review=True),
            map_record("Candidate", "W5", in_scope=False),
        ]
        exclusion = {column: "" for column in PAPER_EXCLUSION_COLUMNS}
        exclusion.update({
            "exclusion_id": "excluded-one",
            "title": excluded["title"],
            "year": str(excluded["year"]),
            "openalex_url": excluded["openalex_url"],
            "reason": "out_of_scope",
            "excluded_from_public_preview": "true",
            "excluded_from_map": "true",
            "is_active": "true",
        })
        root, map_path, exclusions_path, links_path = self.workspace(records, [exclusion])
        queried = []
        stats = autofill_public_map_arxiv_ids(
            map_path=map_path,
            links_path=links_path,
            exclusions_path=exclusions_path,
            lookup=lambda title: queried.append(title) or [],
        )
        self.assertEqual(queried, ["Eligible"])
        self.assertEqual(stats["total_records"], 1)
        self.assertNotIn("Absent from map", queried)

    def test_match_writes_curated_override_and_export_consumes_it(self):
        record = map_record("Exact Public Paper", "W9")
        root, map_path, exclusions_path, links_path = self.workspace([record])
        exports = []
        stats = autofill_public_map_arxiv_ids(
            map_path=map_path,
            links_path=links_path,
            exclusions_path=exclusions_path,
            lookup=lambda title: [{"title": title, "arxiv_id": "2501.99999v2"}],
            export=lambda: exports.append(True) or {"success": True},
        )
        with links_path.open(encoding="utf-8", newline="") as handle:
            override = next(csv.DictReader(handle))
        self.assertEqual(override["openalex_url"], record["openalex_url"])
        self.assertEqual(override["arxiv_id"], "2501.99999")
        self.assertEqual(exports, [True])
        exported = dict(record)
        apply_paper_arxiv_links([exported], [override])
        self.assertEqual(exported["arxiv_id"], "2501.99999")
        self.assertEqual(exported["paper_url"], "https://arxiv.org/pdf/2501.99999.pdf")
        self.assertTrue(stats["export_ran"])

    def test_eligibility_helper_uses_map_canonical_identity(self):
        one = map_record("Same paper", "W20")
        duplicate = {**one, "id": "second-marker", "institution": "Second"}
        papers = eligible_public_map_papers([one, duplicate])
        self.assertEqual(len(papers), 1)

    def test_progress_increases_and_failure_does_not_stop_later_paper(self):
        records = [map_record("Stalled", "W30"), map_record("Later", "W31")]
        root, map_path, exclusions_path, links_path = self.workspace(records)
        snapshots = []

        def lookup(title):
            if title == "Stalled":
                raise ArxivLookupError("timeout", kind="timeout", attempts=3)
            return [{"title": title, "arxiv_id": "2501.33333"}]

        stats = autofill_public_map_arxiv_ids(
            map_path=map_path,
            links_path=links_path,
            exclusions_path=exclusions_path,
            lookup=lookup,
            progress=lambda state: snapshots.append(dict(state)),
        )
        processed = [state["processed_lookups"] for state in snapshots]
        self.assertIn(1, processed)
        self.assertIn(2, processed)
        self.assertEqual(stats["failed_lookup_count"], 1)
        self.assertEqual(stats["exact_matches_added"], 1)


class ArxivAutofillEndpointTests(unittest.TestCase):
    @contextlib.contextmanager
    def server(self, runner):
        with ARXIV_AUTOFILL_STATE_LOCK:
            ARXIV_AUTOFILL_STATE.update({
                "status": "idle",
                "total_eligible_papers": 0,
                "papers_requiring_lookup": 0,
                "processed_lookups": 0,
                "exact_matches_added": 0,
                "no_matches": 0,
                "ambiguous_matches": 0,
                "failed_lookups": 0,
                "current_paper_title": "",
                "start_time": None,
                "completion_time": None,
                "final_error": "",
                "result": None,
            })
        server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            make_handler("test-token", autofill_runner=runner),
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def request(self, base_url, path, method="GET"):
        request = urllib.request.Request(
            base_url + path,
            data=b"{}" if method == "POST" else None,
            method=method,
            headers={"X-Admin-Token": "test-token", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=2) as response:
            return response.status, json.loads(response.read())

    def test_post_returns_promptly_status_runs_completes_and_duplicate_is_409(self):
        release = threading.Event()

        def runner(export, progress):
            progress({
                "eligible_public_map_papers": 2,
                "papers_requiring_lookup": 2,
                "processed_lookups": 1,
                "exact_matches_added": 0,
                "no_match_count": 1,
                "ambiguous_match_count": 0,
                "failed_lookup_count": 0,
                "current_paper_title": "Second paper",
            })
            release.wait(timeout=2)
            return {
                "eligible_public_map_papers": 2,
                "papers_requiring_lookup": 2,
                "processed_lookups": 2,
                "exact_matches_added": 1,
                "no_match_count": 1,
                "ambiguous_match_count": 0,
                "failed_lookup_count": 0,
                "updated_papers": [],
                "failed_lookups": [],
                "export_ran": False,
            }

        with self.server(runner) as base_url:
            started = time.monotonic()
            status, _payload = self.request(
                base_url, "/api/admin/papers/autofill-arxiv", "POST"
            )
            self.assertEqual(status, 202)
            self.assertLess(time.monotonic() - started, 1)
            _status, running = self.request(
                base_url, "/api/admin/papers/autofill-arxiv/status"
            )
            self.assertEqual(running["status"], "running")
            self.assertEqual(running["processed_lookups"], 1)
            with self.assertRaises(urllib.error.HTTPError) as duplicate:
                self.request(base_url, "/api/admin/papers/autofill-arxiv", "POST")
            self.assertEqual(duplicate.exception.code, 409)
            release.set()
            deadline = time.monotonic() + 2
            completed = running
            while completed["status"] == "running" and time.monotonic() < deadline:
                time.sleep(0.01)
                _status, completed = self.request(
                    base_url, "/api/admin/papers/autofill-arxiv/status"
                )
            self.assertEqual(completed["status"], "completed")
            self.assertIsNotNone(completed["completion_time"])


class ArxivAdminFrontendTests(unittest.TestCase):
    def test_admin_button_loading_stats_and_duplicate_guard(self):
        source = (Path(__file__).resolve().parents[1] / "web" / "admin.js").read_text()
        html = (Path(__file__).resolve().parents[1] / "web" / "admin.html").read_text()
        self.assertIn("Find candidates", html)
        validation = html.split("<summary>Validation</summary>", 1)[1].split(
            "</div></details>", 1
        )[0]
        self.assertNotIn("arXiv", validation)
        body = source.split("async function autofillArxivIds()", 1)[1]
        self.assertIn("if (button.disabled) return", body)
        self.assertIn('button.textContent = "Finding candidates…"', body)
        self.assertIn("No curated links were changed", body)

    def test_page_reload_resumes_polling_and_terminal_states_restore_button(self):
        source = (Path(__file__).resolve().parents[1] / "web" / "admin.js").read_text()
        load_body = source.split("async function loadApplication(", 1)[1].split("\nasync function loadDashboardAndQueues", 1)[0]
        self.assertIn('autofillStatus.status === "running"', load_body)
        self.assertIn("scheduleArxivAutofillPoll()", load_body)
        polling = source.split("async function pollArxivAutofillStatus()", 1)[1].split("\nasync function reloadPreviewData", 1)[0]
        self.assertIn("restoreArxivAutofillButton()", polling)
        self.assertIn('status.status === "completed"', polling)
        self.assertIn('status.status === "failed"', polling)
        self.assertIn("1500", source)

    def test_public_links_render_user_facing_paper_versions(self):
        source = (Path(__file__).resolve().parents[1] / "web" / "app.js").read_text()
        body = source.split("function paperExternalLinks(", 1)[1].split("\nfunction escapeCsvValue", 1)[0]
        self.assertIn("`https://arxiv.org/abs/${arxivId}`", body)
        self.assertNotIn("recordArxivUrl(record)", body)
        self.assertNotIn('label: "DOI"', body)
        self.assertIn("PaperLinkHelpers.paperVersionLinks(record, safeArxivUrl)", body)
        self.assertIn('arxivId\n    ? safeHttpUrl', body)
