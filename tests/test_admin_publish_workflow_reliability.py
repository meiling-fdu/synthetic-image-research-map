import http.client
import json
import socket
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest import mock

from scripts import admin_workflows
from scripts.serve_admin import make_handler


TOKEN = "publish-reliability-test-token"


def success_result(duration=188.0):
    return {
        "success": True,
        "command": ["python3 scripts/admin_publish_changes.py"],
        "exit_code": 0,
        "stdout_tail": "Publish Changes completed successfully.",
        "stderr_tail": "",
        "duration_seconds": duration,
        "changed_files": [],
        "steps": [],
        "failed_stage": "",
        "error_summary": "",
        "timed_out": False,
        "failure_kind": "",
    }


def request(server, path, *, body=None):
    connection = http.client.HTTPConnection(
        "127.0.0.1", server.server_port, timeout=3
    )
    headers = {"X-Admin-Token": TOKEN}
    encoded = None
    if body is not None:
        encoded = json.dumps(body)
        headers["Content-Type"] = "application/json"
    connection.request("POST" if body is not None else "GET", path, encoded, headers)
    response = connection.getresponse()
    payload = json.loads(response.read())
    connection.close()
    return response.status, payload


class RunningServer:
    def __init__(self, runner):
        self.server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            make_handler(TOKEN, workflow_runner=runner, geocoder=object()),
        )
        self.thread = threading.Thread(
            target=self.server.serve_forever, daemon=True
        )

    def __enter__(self):
        self.thread.start()
        return self.server

    def __exit__(self, *_args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)


class AdminPublishWorkflowReliabilityTests(unittest.TestCase):
    def test_error_summary_prefers_concrete_validator_error(self):
        summary = admin_workflows._error_summary(
            "ERROR: Refresh reported validation errors:\n"
            "  ERROR: institution_review_queue.csv: concrete integrity failure\n"
            "ERROR: Refresh failed with exit code 1 after 2s.\n"
            "ERROR: publishing stopped during refresh.\n",
            "",
        )
        self.assertEqual(
            summary,
            "ERROR: institution_review_queue.csv: concrete integrity failure",
        )

    def test_long_success_propagates_without_false_timeout(self):
        def runner(name, *, progress):
            self.assertEqual(name, "publish_changes")
            progress({
                "stage": "Refresh: python3 scripts/export_public_preview.py --preserve-existing",
                "command": "python3 scripts/export_public_preview.py --preserve-existing",
                "elapsed_seconds": 97.0,
            })
            return success_result()

        with RunningServer(runner) as server:
            status, payload = request(
                server,
                "/api/publish-changes",
                body={"confirmed": True},
            )

        self.assertEqual(status, 200)
        self.assertTrue(payload["success"])
        self.assertEqual(payload["duration_seconds"], 188.0)
        self.assertFalse(payload["timed_out"])

    def test_nonzero_export_result_preserves_stage_exit_and_summary(self):
        failure = success_result()
        failure.update({
            "success": False,
            "exit_code": 7,
            "failed_stage": (
                "Refresh: python3 scripts/export_public_preview.py "
                "--preserve-existing"
            ),
            "error_summary": "ERROR: controlled export failure",
            "failure_kind": "subprocess_exit",
        })

        with RunningServer(lambda _name, *, progress: failure) as server:
            status, payload = request(
                server,
                "/api/publish-changes",
                body={"confirmed": True},
            )

        self.assertEqual(status, 200)
        self.assertFalse(payload["success"])
        self.assertEqual(payload["exit_code"], 7)
        self.assertIn("export_public_preview.py", payload["failed_stage"])
        self.assertEqual(
            payload["error_summary"], "ERROR: controlled export failure"
        )

    def test_duplicate_publish_is_rejected_while_first_is_active(self):
        started = threading.Event()
        release = threading.Event()
        calls = []

        def runner(name, *, progress):
            calls.append(name)
            started.set()
            release.wait(timeout=3)
            return success_result()

        with RunningServer(runner) as server:
            first_result = {}

            def first_request():
                first_result["response"] = request(
                    server,
                    "/api/publish-changes",
                    body={"confirmed": True},
                )

            thread = threading.Thread(target=first_request)
            thread.start()
            self.assertTrue(started.wait(timeout=2))
            duplicate_status, duplicate = request(
                server,
                "/api/publish-changes",
                body={"confirmed": True},
            )
            release.set()
            thread.join(timeout=3)

        self.assertEqual(duplicate_status, 409)
        self.assertIn("already running", duplicate["error"])
        self.assertEqual(calls, ["publish_changes"])
        self.assertTrue(first_result["response"][1]["success"])

    def test_closed_connection_does_not_change_completed_success_status(self):
        started = threading.Event()
        release = threading.Event()

        def runner(_name, *, progress):
            started.set()
            release.wait(timeout=3)
            return success_result()

        with RunningServer(runner) as server:
            client = socket.create_connection(
                ("127.0.0.1", server.server_port), timeout=2
            )
            body = b'{"confirmed":true}'
            client.sendall(
                b"POST /api/publish-changes HTTP/1.1\r\n"
                + f"Host: 127.0.0.1:{server.server_port}\r\n".encode()
                + f"X-Admin-Token: {TOKEN}\r\n".encode()
                + b"Content-Type: application/json\r\n"
                + f"Content-Length: {len(body)}\r\n\r\n".encode()
                + body
            )
            self.assertTrue(started.wait(timeout=2))
            client.close()
            release.set()

            for _attempt in range(50):
                status, snapshot = request(
                    server, "/api/latest-validation-status"
                )
                if snapshot["state"] != "running":
                    break
                threading.Event().wait(0.01)

        self.assertEqual(status, 200)
        self.assertEqual(snapshot["state"], "succeeded")
        self.assertTrue(snapshot["result"]["success"])

    def test_publish_uses_long_timeout_for_controlled_long_result(self):
        controlled = {
            **success_result(),
            "command": "python3 scripts/admin_publish_changes.py",
            "stage": "Completed",
        }
        with mock.patch.object(
            admin_workflows, "_run", return_value=controlled
        ) as run:
            result = admin_workflows.run_workflow("publish_changes")

        self.assertTrue(result["success"])
        publish_call = next(
            call
            for call in run.call_args_list
            if call.args[0] == admin_workflows.PUBLISH_CHANGES
        )
        self.assertEqual(
            publish_call.kwargs["timeout"],
            admin_workflows.PUBLISH_TIMEOUT_SECONDS,
        )
        self.assertGreater(
            admin_workflows.PUBLISH_TIMEOUT_SECONDS, 188
        )


if __name__ == "__main__":
    unittest.main()
