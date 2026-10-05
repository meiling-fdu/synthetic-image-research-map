"""Verified pre-gap inputs for completed historical audit reports.

Historical reports retain their original 623-paper input layer after the approved
gap migration. Current-corpus invariants are checked separately by the migration
validator and repository tests. No frozen NeurIPS artifact is redirected/edited.
"""
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'data/raw/systematic_gap_migration_2026_10_03'


def historical_bytes(path):
    path = Path(path).resolve()
    try:
        relative = path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.read_bytes()
    if not (EVIDENCE / 'insertion.json').exists():
        return path.read_bytes()
    manifest = json.loads((EVIDENCE / 'predecessor_623_manifest.json').read_text())
    entry = manifest.get(relative)
    if entry is None:
        # Files untouched by the gap migration can still change in a later
        # approved successor. Replay their verified pre-Batch-A bytes without
        # changing the older 623/666-paper snapshots or their receipts.
        try:
            from .corpus_quality_history import historical_bytes as batch_a_bytes
        except ImportError:
            from corpus_quality_history import historical_bytes as batch_a_bytes
        return batch_a_bytes(path)
    baseline = json.loads((EVIDENCE / 'baseline.json').read_text())
    if entry['sha256'] != baseline['tracked_sha256'][relative]:
        raise AssertionError('Historical input disagrees with pre-migration baseline: ' + relative)
    with gzip.open(EVIDENCE / entry['archive'], 'rb') as handle:
        value = handle.read()
    if hashlib.sha256(value).hexdigest() != entry['sha256']:
        raise AssertionError('Historical input archive checksum mismatch: ' + relative)
    return value


def historical_text(path, encoding='utf-8'):
    return historical_bytes(path).decode(encoding)
