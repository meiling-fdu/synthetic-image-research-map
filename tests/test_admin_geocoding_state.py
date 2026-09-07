import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GeocodingStateTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node.js required')
    def test_modal_state_transitions_and_guarded_application(self):
        subprocess.run(['node', 'tests/admin_geocoding_state.cjs'], cwd=ROOT, check=True,
                       capture_output=True, text=True)
