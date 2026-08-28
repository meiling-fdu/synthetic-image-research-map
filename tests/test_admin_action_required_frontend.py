import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node") or str(Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node")


class ActionRequiredFrontendTests(unittest.TestCase):
    def test_runtime_summary_navigation_and_refresh_invariants(self):
        result = subprocess.run([NODE, "tests/admin_action_required_frontend.cjs"],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
