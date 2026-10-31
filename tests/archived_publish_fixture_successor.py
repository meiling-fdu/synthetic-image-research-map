"""Load the authenticated, superseded R2 protocol without changing live guards."""
import hashlib
import json
from pathlib import Path
from types import ModuleType
import uuid

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = "data/raw/corpus_quality_batch_b_wave_b5_01_2026_10_30/fixture_successor_archive"
MANIFEST_SHA256 = "f8ed721670d485bc96f408031a005ef20fea5d3a15a996ccb72a9e4a5748e47b"


def load_archived_successor(root=ROOT):
    archive = (Path(root) / ARCHIVE).resolve()
    manifest_bytes = (archive / "archive_manifest.json").read_bytes()
    assert hashlib.sha256(manifest_bytes).hexdigest() == MANIFEST_SHA256, "Unreviewed R2 archive manifest"
    manifest = json.loads(manifest_bytes)
    assert manifest["status"] == "ARCHIVAL_ONLY_NOT_CURRENT_RUNTIME_AUTHORIZATION"
    actual = {str(p.relative_to(archive)) for p in archive.rglob("*") if p.is_file()}
    assert actual == set(manifest["files"]) | {"archive_manifest.json"}, "Unexpected R2 archive file inventory"
    verified = {}
    for relative, entry in manifest["files"].items():
        raw = (archive / relative).read_bytes()
        assert len(raw) == entry["bytes"] and hashlib.sha256(raw).hexdigest() == entry["sha256"], "Unreviewed R2 archive source: " + relative
        verified[relative] = raw
    source = archive / "tests/public_refinement_snapshot.py"
    history = ModuleType("archived_b5_r2_" + uuid.uuid4().hex)
    history.__file__ = str(source)
    exec(compile(verified["tests/public_refinement_snapshot.py"], str(source), "exec"), history.__dict__)
    assert history.ROOT == archive
    return history
