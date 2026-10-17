"""Replay completed literature checks at their immutable published endpoint.

The live successor is independently checked by the B1D transaction regressions.
This local-only temporary clone shares object storage read-only; scientific
check/apply functions receive its root explicitly and never write this checkout.
"""
import atexit
from functools import lru_cache
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED_ENDPOINT = "8e60ee5729ab0b29703078b91cf83fb245048f6c"


@lru_cache
def published_literature_endpoint():
    root = Path(tempfile.mkdtemp(prefix="literature51-published-"))
    atexit.register(shutil.rmtree, root, ignore_errors=True)
    # Clone only committed local history. No remote access or primary writes.
    subprocess.run(["git", "clone", "--quiet", "--shared", "--no-checkout",
                    str(ROOT), str(root)], check=True, capture_output=True)
    subprocess.run(["git", "checkout", "--quiet", "--detach", PUBLISHED_ENDPOINT],
                   cwd=root, check=True, capture_output=True)
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                   text=True).strip() == PUBLISHED_ENDPOINT
    assert not subprocess.check_output(["git", "status", "--porcelain=v1", "-uall"], cwd=root)
    from scripts.literature51_reproducibility import materialize_export_inputs
    materialize_export_inputs(root)  # Committed, checksum-verified inputs only.
    return root
