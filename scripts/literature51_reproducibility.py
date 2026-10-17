"""Keep local-workspace preservation distinct from a self-contained checkout.

The 130 unrelated untracked inputs never belong to the literature commit.
When present, every one is required and hash-checked. A checkout without them
must instead prove its exact tracked inventory and absence of all local-only
payloads. Paper, taxonomy, primary-source and history checks are unchanged.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path('data/processed/literature51_2026_10_16')
PREFLIGHT = OUT/'followup/commit_preflight.json'


def preserved_bytes(root, relative):
    """Read exact historical receipt bytes, including lossless commit archives."""
    path = root/relative
    if path.exists():
        return path.read_bytes()
    preflight = json.loads((root/PREFLIGHT).read_text())
    archive = preflight['lossless_archives'].get(relative)
    if archive is None:
        raise FileNotFoundError(path)
    content = gzip.decompress((root/archive['path']).read_bytes())
    assert hashlib.sha256(content).hexdigest()==archive['original_sha256'],relative
    return content


def preserved_digest(root, relative):
    return hashlib.sha256(preserved_bytes(root,relative)).hexdigest()


def materialize_export_inputs(root):
    """Restore committed, hash-verified legacy inputs for unchanged validators.

    These legacy export and historical-test inputs were not tracked in the
    original workspace. Reproduction uses only committed lossless archives,
    never local caches. Existing files must match; nothing is overwritten.
    """
    preflight = json.loads((root/PREFLIGHT).read_text())
    results = []
    for relative, source in preflight['reproduction_inputs'].items():
        assert relative.startswith(('data/processed/','web/data/')) or relative=='data/manual/institution_consistency_audit.csv'
        if source.get('kind')=='historical_protected_input':
            history=json.loads((root/'data/raw/systematic_gap_migration_2026_10_03/baseline.json').read_text())
            assert source['original_sha256']==(history['protected_105']|history['frozen_sha256'])[relative]
        content = gzip.decompress((root/source['path']).read_bytes())
        assert hashlib.sha256(content).hexdigest()==source['original_sha256'],relative
        target=root/relative
        if target.exists():
            assert target.read_bytes()==content,'Reproduction input differs: '+relative
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(content)
        results.append(relative)
    return results


def verify_workspace_files(root, expected, *, require_present=False):
    """Validate either the original workspace or the approved isolated checkout.

    A partially present or modified workspace fails. A repository checkout may
    omit all workspace-only inputs only when the committed preflight manifest
    explicitly excludes them and its complete tracked inventory is verified.
    """
    successor = root/OUT/'main_integration/manifest.json'
    if successor.exists() and not require_present:
        # Some previously untracked audit documents are now published upstream.
        # Verify their committed upstream bytes; never require copying local files.
        from scripts.verify_literature51_main_integration import verify_inventory
        manifest = verify_inventory(root)
        remote = set(subprocess.check_output(['git','ls-tree','-r','--name-only',manifest['remote_base']],cwd=root).decode().splitlines())
        assert all(not (root/p).exists() for p in set(expected)-remote), 'Unexpected local workspace file'
        return 'isolated_checkout_local_files_absent'
    present = [p for p in expected if (root/p).exists()]
    if require_present or present:
        assert len(present)==len(expected),'Incomplete pre-existing local workspace'
        assert all(preserved_digest(root,p)==h for p,h in expected.items()),'Pre-existing local file changed'
        return 'original_workspace_hashes_verified'

    preflight = json.loads((root/PREFLIGHT).read_text())
    assert preflight['workspace_only_sha256']==expected
    baseline = json.loads((root/OUT/'baseline.json').read_text())
    approved = (root/OUT/'followup/proposed_staging.txt').read_text().splitlines()
    assert len(approved)==len(set(approved))
    tracked = set(subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().rstrip('\0').split('\0'))
    assert tracked==set(baseline['tracked_sha256'])|set(approved),'Unexpected checkout inventory'
    assert not tracked.intersection(expected),'Workspace-only evidence entered the commit'
    assert all((root/p).is_file() for p in approved),'Missing committed dependency'
    assert all(not (root/p).exists() for p in preflight['excluded_local_paths']),'Local-only payload in snapshot'
    return 'isolated_checkout_local_files_absent'
