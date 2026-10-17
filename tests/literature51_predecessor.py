"""Checksum-verified pre-import inputs for completed historical regression tests.

Only historical tests opt in. Production readers and current-corpus tests keep
reading the actual successor. No historical counts or receipts are rewritten.
"""
from copy import deepcopy
import csv
from functools import lru_cache
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/processed/literature51_2026_10_16'


@lru_cache
def predecessor_bytes(relative):
    baseline = json.loads((OUT/'baseline.json').read_text())
    expected = baseline['tracked_sha256'][relative]
    archive = OUT/(Path(relative).name+'.before.gz')
    if archive.exists():
        value = gzip.decompress(archive.read_bytes())
    else:
        value = (ROOT/relative).read_bytes()
        if hashlib.sha256(value).hexdigest()!=expected:
            value = subprocess.check_output(['git','show',baseline['head']+':'+relative],cwd=ROOT)
    if hashlib.sha256(value).hexdigest()!=expected:
        raise AssertionError('Pre-import snapshot checksum mismatch: '+relative)
    return value


def predecessor_rows(relative):
    return list(csv.DictReader(io.StringIO(predecessor_bytes(relative).decode('utf-8-sig'),newline='')))


@lru_cache
def _context():
    from scripts.validate_corpus_quality_audit import load_context as current_context
    with tempfile.TemporaryDirectory(prefix='literature51-predecessor-') as name:
        root=Path(name)
        for relative in ('web/data/public_preview_papers.json','web/data/public_preview_map_data.json',
                         'data/curated/paper_taxonomy.csv','data/curated/institutions.csv',
                         'data/manual/neurips_2026_targeted_gap_fill_reconciliation.json'):
            target=root/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(predecessor_bytes(relative))
        return current_context(root)


def load_context():
    return deepcopy(_context())


@lru_cache
def _main_context():
    """Replay the immutable published-main receipt before the literature delta."""
    from scripts.validate_corpus_quality_audit import load_context as current_context
    from scripts.verify_literature51_main_integration import baseline_bytes
    with tempfile.TemporaryDirectory(prefix='literature51-main-predecessor-') as name:
        root = Path(name)
        for relative in ('web/data/public_preview_papers.json', 'web/data/public_preview_map_data.json',
                         'data/curated/paper_taxonomy.csv', 'data/curated/institutions.csv',
                         'data/manual/neurips_2026_targeted_gap_fill_reconciliation.json'):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(baseline_bytes(ROOT, relative))
        return current_context(root)


def load_main_baseline_context():
    return deepcopy(_main_context())


def main_baseline_constants():
    from scripts.verify_literature51_main_integration import baseline_bytes
    namespace = {}
    # This is fixed, already-published Python containing only baseline constants.
    exec(compile(baseline_bytes(ROOT, 'tests/baseline_expectations.py'), '<published main baseline>', 'exec'), namespace)
    return namespace
