"""Per-instance sync ownership for the unchanged legacy publish HTTP tests."""
from pathlib import Path
import tempfile


def isolated_publish_server(endpoint):
    """Extend only a selected test module's server; never patch production globals."""
    original = endpoint.RunningServer

    class IsolatedRunningServer(original):
        def __init__(self, runner):
            self.temporary = tempfile.TemporaryDirectory()
            handler = None
            self.server = None
            try:
                handler = endpoint.make_handler(
                    endpoint.TOKEN, workflow_runner=runner, geocoder=object(),
                    public_preview_sync_state_path=Path(self.temporary.name) / "sync.json",
                )
                self.server = endpoint.ThreadingHTTPServer(("127.0.0.1", 0), handler)
                self.thread = endpoint.threading.Thread(
                    target=self.server.serve_forever, daemon=True,
                )
            except BaseException:
                try:
                    if self.server is not None:
                        self.server.server_close()
                finally:
                    try:
                        if handler is not None:
                            handler.public_preview_sync.close()
                    finally:
                        self.temporary.cleanup()
                raise

        def __enter__(self):
            try:
                return super().__enter__()
            except BaseException:
                try:
                    if self.thread.is_alive():
                        self.server.shutdown()
                        self.thread.join(timeout=3)
                    self.server.server_close()
                finally:
                    self._close_owned_state()
                raise

        def _close_owned_state(self):
            try:
                self.server.RequestHandlerClass.public_preview_sync.close()
            finally:
                self.temporary.cleanup()

        def __exit__(self, *args):
            try:
                return super().__exit__(*args)
            finally:
                self._close_owned_state()

    return IsolatedRunningServer


def install_publish_fixture_isolation(endpoint, monkeypatch):
    """Use pytest's function-scoped rollback for this module-local binding only."""
    isolated = isolated_publish_server(endpoint)
    monkeypatch.setattr(endpoint, "RunningServer", isolated)
    return isolated
