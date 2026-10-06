"""Checksum-verified 640-paper inputs for historical audits and migration tests."""
import base64
from contextlib import contextmanager
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'data/raw/corpus_quality_batch_a_2026_10_04'


def snapshot_bytes():
    manifest = json.loads((EVIDENCE / 'predecessor_640_manifest.json').read_text())
    archive = (EVIDENCE / manifest['archive']).read_bytes()
    if hashlib.sha256(archive).hexdigest() != manifest['sha256']:
        raise ValueError('640-paper snapshot archive checksum mismatch')
    baseline = json.loads((EVIDENCE / 'baseline.json').read_text())
    result = {p: base64.b64decode(v) for p, v in json.loads(gzip.decompress(archive)).items()}
    if set(result) != set(manifest['files']):
        raise ValueError('640-paper snapshot inventory mismatch')
    for path, value in result.items():
        if hashlib.sha256(value).hexdigest() != manifest['files'][path] or manifest['files'][path] != baseline['tracked_sha256'][path]:
            raise ValueError('640-paper snapshot input checksum mismatch: ' + path)
    return result


@lru_cache(maxsize=1)
def _cached_snapshot(manifest_mtime, archive_mtime):
    return snapshot_bytes()


def historical_bytes(path):
    """Read a pre-Batch-A file only when it belongs to the verified snapshot."""
    path=Path(path).resolve()
    try:
        relative=path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.read_bytes()
    manifest=EVIDENCE/'predecessor_640_manifest.json'
    if not manifest.exists():
        return path.read_bytes()
    archive=EVIDENCE/'predecessor_640.json.gz'
    values=_cached_snapshot(manifest.stat().st_mtime_ns,archive.stat().st_mtime_ns)
    return values[relative] if relative in values else path.read_bytes()


def baseline_bytes(path):
    """Read a path exactly as it existed at the verified Batch A baseline."""
    path = Path(path).resolve()
    relative = path.relative_to(ROOT).as_posix()
    manifest = EVIDENCE / 'predecessor_640_manifest.json'
    archive = EVIDENCE / 'predecessor_640.json.gz'
    values = _cached_snapshot(manifest.stat().st_mtime_ns, archive.stat().st_mtime_ns)
    if relative in values:
        return values[relative]
    baseline = json.loads((EVIDENCE / 'baseline.json').read_text())
    expected = baseline['tracked_sha256'].get(relative)
    if not expected:
        return path.read_bytes()
    value = subprocess.check_output(
        ['git', 'show', baseline['head'] + ':' + relative], cwd=ROOT
    )
    if hashlib.sha256(value).hexdigest() != expected:
        raise ValueError('Batch A baseline object checksum mismatch: ' + relative)
    return value


@contextmanager
def predecessor_root():
    """Materialize historical inputs; unchanged protected files stay read-only links."""
    values = snapshot_bytes()
    prior = json.loads((ROOT / 'data/raw/systematic_gap_migration_2026_10_03/baseline.json').read_text())
    with tempfile.TemporaryDirectory(prefix='corpus-640-') as name:
        root = Path(name)
        for path in set(values) | set(prior['protected_105']) | set(prior['frozen_sha256']):
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            if path in values:
                target.write_bytes(values[path])
            else:
                expected = (prior['protected_105'] | prior['frozen_sha256'])[path]
                current = ROOT / path
                if current.is_file() and hashlib.sha256(current.read_bytes()).hexdigest() == expected:
                    target.symlink_to(current)
                else:
                    value = subprocess.check_output(
                        ['git', 'show', prior['head'] + ':' + path], cwd=ROOT
                    )
                    if hashlib.sha256(value).hexdigest() != expected:
                        raise ValueError('historical protected object checksum mismatch: ' + path)
                    target.write_bytes(value)
        yield root
