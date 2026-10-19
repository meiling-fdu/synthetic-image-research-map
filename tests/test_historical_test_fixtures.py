"""Offline provenance, overwrite protection and fixture-tamper regressions."""
import gzip
import hashlib
import json
from pathlib import Path

import pytest

from scripts import restore_historical_test_fixtures as fixtures

ROOT = Path(__file__).resolve().parents[1]


def fixture_tree(root):
    """Use read-only committed sources, with independent temporary destinations."""
    manifest = json.loads((ROOT / fixtures.MANIFEST).read_text())
    preflight = json.loads((ROOT / fixtures.PREFLIGHT).read_text())
    sources = {str(fixtures.MANIFEST), str(fixtures.PREFLIGHT),
               "data/raw/systematic_gap_migration_2026_10_03/baseline.json"}
    sources.update(manifest["authorities"])
    sources.update(e["source"] for e in manifest["entries"])
    sources.update(e["path"] for e in preflight["reproduction_inputs"].values())
    for source in sources:
        target = root / source
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(ROOT / source)
    return root


@pytest.fixture(scope="module")
def materialized(tmp_path_factory):
    root = fixture_tree(tmp_path_factory.mktemp("offline-historical-fixtures"))
    receipt = fixtures.restore(root)
    assert receipt["created"] == receipt["verified_inputs"] == 117
    return root


def test_complete_offline_fixture_inventory_and_idempotence(materialized):
    before = {p: (materialized / p).stat().st_mtime_ns
              for p in fixtures.restore(materialized, check=True)["sha256"]}
    receipt = fixtures.restore(materialized)
    assert receipt["created"] == 0
    assert receipt["legacy_inputs"] == 14 and receipt["historical_inputs"] == 103
    assert before == {p: (materialized / p).stat().st_mtime_ns for p in before}
    for path, expected in receipt["sha256"].items():
        assert hashlib.sha256((materialized / path).read_bytes()).hexdigest() == expected


OS_PATHS = [e["path"] for e in json.loads((ROOT / fixtures.MANIFEST).read_text())["entries"]
            if e["compression"] == "gzip"]
RAW_PATH = next(e["path"] for e in json.loads((ROOT / fixtures.MANIFEST).read_text())["entries"]
                if e["compression"] == "none")
LEGACY_PATH = "data/processed/openalex_candidate_papers.csv"


@pytest.mark.parametrize("relative", OS_PATHS + [RAW_PATH, LEGACY_PATH])
def test_changed_restored_input_is_rejected_and_never_overwritten(materialized, relative):
    target = materialized / relative
    before = target.read_bytes()
    try:
        target.write_bytes(before + b"tampered")
        with pytest.raises(fixtures.FixtureError, match="refusing overwrite"):
            fixtures.restore(materialized)
        assert target.read_bytes() == before + b"tampered"
    finally:
        target.write_bytes(before)


@pytest.mark.parametrize("kind", ["missing_archive", "corrupt_archive", "missing_response", "corrupt_response"])
def test_missing_or_corrupt_committed_source_fails_before_any_write(tmp_path, kind):
    root = fixture_tree(tmp_path)
    entries = fixtures.manifest_entries(root)
    entry = next(e for e in entries if e["compression"] == ("gzip" if "archive" in kind else "none"))
    source = root / entry["source"]
    source.unlink()  # Remove only this temporary link, never the committed source.
    if kind.startswith("corrupt"):
        source.write_bytes(b"corrupt")
    with pytest.raises(fixtures.FixtureError, match="Missing/unreadable|checksum mismatch"):
        fixtures.restore(root)
    assert all(not (root / e["path"]).exists() for e in entries)
    assert not (root / LEGACY_PATH).exists()


@pytest.mark.parametrize("tamper", ["digest", "inventory", "path_escape", "authority"])
def test_manifest_cannot_redefine_historical_authority(tmp_path, tamper):
    root = fixture_tree(tmp_path)
    path = root / fixtures.MANIFEST
    content = json.loads(path.read_text())
    if tamper == "digest":
        content["entries"][0]["sha256"] = "0" * 64
    elif tamper == "inventory":
        content["entries"].pop()
    elif tamper == "path_escape":
        content["entries"][0]["source"] = "../outside"
    else:
        content["authorities"][fixtures.OS_AUTHORITY] = "0" * 64
    path.unlink()
    path.write_text(json.dumps(content))
    with pytest.raises(fixtures.FixtureError):
        fixtures.restore(root)
    assert not (root / LEGACY_PATH).exists()


def test_check_requires_materialization_but_does_not_create_inputs(tmp_path):
    root = fixture_tree(tmp_path)
    with pytest.raises(fixtures.FixtureError, match="not materialized"):
        fixtures.restore(root, check=True)
    assert not (root / LEGACY_PATH).exists()


def test_destination_symlink_cannot_write_outside_the_checkout(tmp_path):
    root = fixture_tree(tmp_path / "checkout")
    outside = tmp_path / "outside"
    outside.mkdir()
    target = root / "data/raw/openalex"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(outside, target_is_directory=True)
    with pytest.raises(fixtures.FixtureError, match="escapes checkout"):
        fixtures.restore(root)
    assert not list(outside.iterdir())


def test_os_archive_bytes_match_both_frozen_authorities():
    entries = fixtures.manifest_entries(ROOT)
    os_entries = [e for e in entries if e["compression"] == "gzip"]
    assert len(os_entries) == 4 and len({e["source"] for e in os_entries}) == 3
    for entry in os_entries:
        body = gzip.decompress((ROOT / entry["source"]).read_bytes())
        assert hashlib.sha256(body).hexdigest() == entry["sha256"]
        assert body[:8] == b"\0\0\0\x01Bud1"
