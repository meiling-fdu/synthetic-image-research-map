import contextlib
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from scripts.serve_admin import STATIC_ROUTES, make_handler


ROOT = Path(__file__).resolve().parents[1]


class AdminAuthenticationFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web" / "admin.html").read_text(encoding="utf-8")
        cls.javascript = (ROOT / "web" / "admin.js").read_text(encoding="utf-8")

    def test_api_fetch_errors_include_request_path_status_and_payload(self):
        api_fetch = self.javascript.split("async function apiFetch(", 1)[1].split(
            "\nfunction isAuthenticationFailure", 1
        )[0]
        self.assertIn("error.name = \"AdminApiError\"", api_fetch)
        self.assertIn("error.path = path", api_fetch)
        self.assertIn("error.status = response.status", api_fetch)
        self.assertIn("error.payload = payload", api_fetch)
        self.assertIn("`${path} failed with HTTP ${response.status}: ${serverMessage}`", api_fetch)

    def test_query_token_is_persisted_before_url_cleanup_and_loading(self):
        token_bootstrap = self.javascript.split("const query = new URLSearchParams", 1)[1].split(
            'elements["search-input"].addEventListener', 1
        )[0]
        self.assertLess(
            token_bootstrap.index('sessionStorage.setItem("adminToken", state.token)'),
            token_bootstrap.index("history.replaceState"),
        )
        self.assertLess(
            token_bootstrap.index("history.replaceState"),
            self.javascript.index("if (state.token) loadApplication();"),
        )

    def test_valid_startup_reveals_workspace_without_requiring_token_panel(self):
        load_body = self.javascript.split("async function loadApplication(", 1)[1].split(
            "\nasync function loadDashboardAndQueues", 1
        )[0]
        self.assertIn('elements["token-panel"].hidden = true', load_body)
        self.assertIn("elements.workspace.hidden = false", load_body)
        self.assertIn("setConnection(\"ok\", \"● Local curation connected\")", load_body)
        self.assertNotIn('requestToken(`Could not load admin data', load_body)

    def test_invalid_startup_token_clears_storage_and_prompts_for_token(self):
        reject_token = self.javascript.split("function rejectCurrentToken", 1)[1].split(
            "\nfunction reportApplicationLoadFailure", 1
        )[0]
        self.assertIn('sessionStorage.removeItem("adminToken")', reject_token)
        self.assertIn('state.token = ""', reject_token)
        self.assertIn("requestToken(message)", reject_token)
        load_body = self.javascript.split("async function loadApplication(", 1)[1].split(
            "\nasync function loadDashboardAndQueues", 1
        )[0]
        self.assertIn("if (isAuthenticationFailure(error))", load_body)
        self.assertIn("rejectCurrentToken()", load_body)

    def test_non_auth_api_failures_keep_token_and_identify_endpoint(self):
        failure_report = self.javascript.split("function reportApplicationLoadFailure", 1)[1].split(
            "\nasync function loadApplication", 1
        )[0]
        self.assertIn('const path = error?.path ? ` (${error.path})` : ""', failure_report)
        self.assertIn('elements["token-panel"].hidden = true', failure_report)
        self.assertIn("showNotice(`${stage}${path}: ${detail}`, \"error\")", failure_report)
        self.assertNotIn("sessionStorage.removeItem", failure_report)
        self.assertNotIn("requestToken", failure_report)

    def test_rendering_failures_are_reported_as_frontend_failures(self):
        load_body = self.javascript.split("async function loadApplication(", 1)[1].split(
            "\nasync function loadDashboardAndQueues", 1
        )[0]
        self.assertIn(
            'reportApplicationLoadFailure("Frontend rendering failed while opening Admin workspace", error)',
            load_body,
        )
        self.assertIn(
            'reportApplicationLoadFailure("Could not finish loading Admin review queues", error)',
            load_body,
        )
        self.assertNotIn("That token was not accepted", load_body)

    def test_delayed_polling_401_is_reported_without_erasing_session(self):
        poll_body = self.javascript.split("async function pollArxivAutofillStatus()", 1)[1].split(
            "\nasync function loadArxivEnrichment", 1
        )[0]
        self.assertIn('showNotice(`Could not read arXiv discovery progress: ${error.message}`, "error")', poll_body)
        self.assertNotIn("sessionStorage.removeItem", poll_body)
        self.assertNotIn("requestToken", poll_body)


class AdminStaticAssetTests(unittest.TestCase):
    @contextlib.contextmanager
    def server(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler("test-token"))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_shared_institution_type_labels_are_served_for_admin_page(self):
        self.assertIn("/institution_type_labels.js", STATIC_ROUTES)
        with self.server() as base_url:
            with urllib.request.urlopen(
                f"{base_url}/institution_type_labels.js?v=20260718-research-institute",
                timeout=3,
            ) as response:
                body = response.read().decode("utf-8")
                cache_control = response.headers.get("Cache-Control")
                content_type = response.headers.get("Content-Type")

        self.assertEqual(response.status, 200)
        self.assertEqual(cache_control, "no-store")
        self.assertEqual(content_type, "text/javascript; charset=utf-8")
        self.assertIn("InstitutionTypeLabels", body)

    def test_admin_static_assets_use_no_store_cache_headers(self):
        with self.server() as base_url:
            for path in ("/admin/", "/admin.js", "/admin.css", "/institution_type_labels.js"):
                with self.subTest(path=path):
                    with urllib.request.urlopen(f"{base_url}{path}", timeout=3) as response:
                        self.assertEqual(response.status, 200)
                        self.assertEqual(response.headers.get("Cache-Control"), "no-store")


if __name__ == "__main__":
    unittest.main()
