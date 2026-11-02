"""Authenticate the original B5-01 endpoint without accepting current-source edits.

Only explicit historical transaction assertions call these readers. Current
acceptances, evidence, identities and B5-02 deltas retain independent live guards.
The complete manifest is pinned; neither working-tree bytes nor a mutable hash
can redefine the historical endpoint.
"""
import hashlib
import json
from pathlib import Path

from tests.corpus_quality_test_helpers import published_bytes, published_context

ROOT = Path(__file__).resolve().parents[1]
B5_01 = "d109c70f6994906ec3d9197baad51cf9d8e51f7c"
MANIFEST = "tests/fixtures/batch_b_b5_01_endpoint.json"
MANIFEST_SHA256 = "22000e8f7fda983e263453781d96f5eae139cfce6ff35f0ad973ac67ca4d1b04"


def authenticated_manifest(root=ROOT):
    assert (B5_01, MANIFEST, MANIFEST_SHA256) == (
        "d109c70f6994906ec3d9197baad51cf9d8e51f7c",
        "tests/fixtures/batch_b_b5_01_endpoint.json",
        "22000e8f7fda983e263453781d96f5eae139cfce6ff35f0ad973ac67ca4d1b04",
    ), "Unreviewed historical endpoint authorization metadata"
    raw = (root / MANIFEST).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == MANIFEST_SHA256, "Unreviewed historical endpoint manifest"
    value = json.loads(raw)
    assert value['schema'] == 1 and value['commit'] == B5_01
    return value


def b5_01_bytes(path):
    manifest = authenticated_manifest()
    assert path in manifest['files'], "Undeclared historical endpoint path"
    raw = published_bytes(B5_01, path)
    assert hashlib.sha256(raw).hexdigest() == manifest['files'][path], "Historical endpoint bytes changed: " + path
    return raw


def b5_01_context():
    # Authenticate every input used by the preferred-ID public-context helper.
    for path in ('data/curated/paper_taxonomy.csv', 'web/data/public_preview_papers.json',
                 'web/data/public_preview_map_data.json'):
        b5_01_bytes(path)
    return published_context(B5_01)
