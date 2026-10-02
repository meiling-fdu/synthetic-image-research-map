"""A completed migration receipt must survive later Git work without losing guards."""

import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts import legacy_scope_exclusion_migration as migration


def manifest_text(manifest):
    return json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


@pytest.mark.parametrize("status", [[], [{"path": "unrelated.txt", "status": "??"}]])
def test_historical_manifest_reproduces_without_live_git(status):
    with patch.object(migration, "git_status_entries", return_value=status) as live:
        first = manifest_text(migration.build_changed_files_manifest())
        second = manifest_text(migration.build_changed_files_manifest())
    live.assert_not_called()
    source = json.loads(migration.CHANGED_STATUS_SNAPSHOT_PATH.read_text())
    assert first == second == migration.CHANGED_MANIFEST_PATH.read_text()
    assert hashlib.sha256(first.encode()).hexdigest() == source["source_sha256"]
    assert len(source["entries"]) == 59


@pytest.mark.parametrize("mutation", ["drop", "add", "status", "source"])
def test_historical_status_snapshot_rejects_tampering(tmp_path, monkeypatch, mutation):
    source = json.loads(migration.CHANGED_STATUS_SNAPSHOT_PATH.read_text())
    if mutation == "drop":
        source["entries"].pop()
    elif mutation == "add":
        source["entries"].append({"path": "unknown.txt", "status": "??"})
    elif mutation == "status":
        source["entries"][0]["status"] = "A "
    else:
        source["source_commit"] = "0" * 40
    path = tmp_path / "status.json"
    path.write_text(manifest_text(source))
    monkeypatch.setattr(migration, "CHANGED_STATUS_SNAPSHOT_PATH", path)
    with pytest.raises(AssertionError, match="snapshot hash mismatch"):
        migration.build_changed_files_manifest()


def test_explicit_live_status_keeps_unknown_and_protected_paths_visible():
    entries = [
        {"path": "data/curated/papers.csv", "status": " M"},
        {"path": "docs/unrelated.md", "status": "??"},
        {"path": "web/app.js", "status": " M"},
    ]
    manifest = migration.build_changed_files_manifest(entries)
    assert manifest["entries"] == entries
    assert manifest["groups"]["unclassified"] == [entry["path"] for entry in entries]
    assert manifest["group_integrity"]["all_entries_classified"] is False
    assert manifest["semantic_boundaries"]["protected_authoritative_files_changed"] == [
        "data/curated/papers.csv"
    ]
    assert manifest["semantic_boundaries"]["frontend_source_files_changed"] == ["web/app.js"]
    assert migration.build_changed_files_manifest([])["counts"]["reported_entries"] == 0


def test_duplicate_status_paths_cannot_be_collapsed():
    entry = {"path": "tests/example.py", "status": " M"}
    with pytest.raises(AssertionError, match="duplicate paths"):
        migration.build_changed_files_manifest([entry, entry])


def test_overlapping_classification_remains_detected(monkeypatch):
    path = "scripts/legacy_scope_exclusion_migration.py"
    monkeypatch.setattr(
        migration, "MANIFEST_IMPLEMENTATION_PATHS",
        migration.MANIFEST_IMPLEMENTATION_PATHS | {path},
    )
    manifest = migration.build_changed_files_manifest()
    assert manifest["group_integrity"]["duplicate_group_entries"] == [path]


@pytest.mark.parametrize("mutation", ["missing", "byte", "path", "group"])
def test_check_current_still_rejects_damaged_manifest(tmp_path, mutation):
    path = tmp_path / "manifest.json"
    if mutation != "missing":
        text = migration.CHANGED_MANIFEST_PATH.read_text()
        if mutation == "byte":
            text += "\n"
        else:
            manifest = json.loads(text)
            if mutation == "path":
                manifest["entries"].pop()
            else:
                manifest["groups"]["A_authoritative_exclusion_changes"] = []
            text = manifest_text(manifest)
        path.write_text(text)
    # Keep ROOT-relative receipt paths intact; intercept only this output read.
    original_path = migration.CHANGED_MANIFEST_PATH
    read_text = Path.read_text
    is_file = Path.is_file

    def read_output(p, *args, **kwargs):
        return read_text(path if p == original_path else p, *args, **kwargs)

    def output_exists(p):
        return is_file(path if p == original_path else p)

    with patch.object(Path, "read_text", read_output), patch.object(Path, "is_file", output_exists):
        with pytest.raises(AssertionError, match="changed-files manifest is (missing|stale)"):
            migration.check_current()
