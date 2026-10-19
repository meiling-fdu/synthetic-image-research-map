#!/usr/bin/env python3
"""Restore authenticated offline test inputs in a disposable repository checkout.

The existing literature materializer remains responsible for its fourteen
legacy inputs. This extends that setup with exact historical OS payloads and
existing committed OpenAlex snapshots, without changing any audit manifest.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

try:
    from .literature51_reproducibility import materialize_export_inputs, PREFLIGHT
except ImportError:
    from literature51_reproducibility import materialize_export_inputs, PREFLIGHT

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path("tests/fixtures/historical_test_fixture_manifest.json")
OS_AUTHORITY = "data/processed/legacy_scope_exclusion_migration_2026_09/predecessor_666_snapshot.json"
RAW_AUTHORITY = "data/processed/workshop_venue_baseline.json"
TIER1 = "data/processed/systematic_tier1_2026_09/baseline/"


class FixtureError(ValueError):
    """Missing, corrupt, conflicting or undeclared historical test input."""


def digest(value):
    return hashlib.sha256(value).hexdigest()


def relative_path(value):
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts or str(path) != value:
        raise FixtureError("Invalid repository-relative fixture path: " + str(value))
    return Path(value)


def read_bytes(path):
    try:
        return path.read_bytes()
    except OSError as error:
        raise FixtureError(f"Missing/unreadable fixture input: {path}: {error}") from error


def read_json(path):
    try:
        return json.loads(read_bytes(path))
    except (ValueError, UnicodeError) as error:
        raise FixtureError(f"Invalid fixture JSON: {path}: {error}") from error


def source_bytes(root, entry):
    source = root / relative_path(entry["source"])
    value = read_bytes(source)
    if digest(value) != entry["source_sha256"]:
        raise FixtureError("Fixture source checksum mismatch: " + entry["source"])
    if entry["compression"] == "gzip":
        try:
            value = gzip.decompress(value)
        except (OSError, EOFError) as error:
            raise FixtureError("Invalid fixture archive: " + entry["source"]) from error
    elif entry["compression"] != "none":
        raise FixtureError("Unknown fixture compression: " + entry["source"])
    if digest(value) != entry["sha256"] or len(value) != entry["bytes"]:
        raise FixtureError("Restored fixture checksum/size mismatch: " + entry["path"])
    return value


def target_path(root, relative):
    target = root / relative_path(relative)
    # A test bootstrap must not follow a destination link into another worktree.
    if target.is_symlink() or not target.resolve().is_relative_to(root.resolve()):
        raise FixtureError("Fixture destination escapes checkout or is a symlink: " + relative)
    return target


def manifest_entries(root):
    manifest = read_json(root / MANIFEST)
    if manifest.get("schema_version") != 1:
        raise FixtureError("Unsupported historical fixture manifest schema")
    authorities = manifest["authorities"]
    if set(authorities) != {OS_AUTHORITY, RAW_AUTHORITY}:
        raise FixtureError("Unexpected historical fixture authorities")
    for relative, expected in authorities.items():
        if digest(read_bytes(root / relative)) != expected:
            raise FixtureError("Historical authority checksum mismatch: " + relative)
    os_hashes = read_json(root / OS_AUTHORITY)["historical_artifact_sha256"]
    raw_hashes = read_json(root / RAW_AUTHORITY)["source_hashes"]
    expected = {p: h for p, h in os_hashes.items() if Path(p).name == ".DS_Store"}
    expected.update({p: h for p, h in raw_hashes.items()
                     if p.startswith("data/raw/openalex/") and p.endswith(".json")})
    entries = manifest["entries"]
    paths = [entry["path"] for entry in entries]
    if len(paths) != len(set(paths)) or set(paths) != set(expected):
        raise FixtureError("Historical fixture inventory differs from immutable authorities")
    for entry in entries:
        relative = entry["path"]
        relative_path(relative)
        relative_path(entry["source"])
        if entry["sha256"] != expected[relative]:
            raise FixtureError("Fixture digest differs from immutable authority: " + relative)
        is_os = Path(relative).name == ".DS_Store"
        authority = OS_AUTHORITY if is_os else RAW_AUTHORITY
        source = ("tests/fixtures/historical_os_metadata/" + expected[relative] + ".gz"
                  if is_os else TIER1 + relative)
        if entry["authority"] != authority or entry["source"] != source:
            raise FixtureError("Unexpected historical fixture source: " + relative)
        if entry["compression"] != ("gzip" if is_os else "none"):
            raise FixtureError("Unexpected historical fixture encoding: " + relative)
    return entries


def legacy_entries(root):
    """Preflight the existing materializer's inputs before allowing any writes."""
    preflight = read_json(root / PREFLIGHT)
    history = read_json(root / "data/raw/systematic_gap_migration_2026_10_03/baseline.json")
    result = []
    for relative, source in preflight["reproduction_inputs"].items():
        if not (relative.startswith(("data/processed/", "web/data/"))
                or relative == "data/manual/institution_consistency_audit.csv"):
            raise FixtureError("Unexpected legacy fixture destination: " + relative)
        if source.get("kind") == "historical_protected_input":
            expected = (history["protected_105"] | history["frozen_sha256"])[relative]
            if expected != source["original_sha256"]:
                raise FixtureError("Legacy fixture differs from protected history: " + relative)
        try:
            body = gzip.decompress(read_bytes(root / relative_path(source["path"])))
        except (OSError, EOFError) as error:
            raise FixtureError("Invalid legacy fixture archive: " + source["path"]) from error
        if digest(body) != source["original_sha256"]:
            raise FixtureError("Legacy fixture checksum mismatch: " + relative)
        result.append({"path": relative, "sha256": source["original_sha256"]})
    return result


def restore(root=ROOT, *, check=False):
    root = Path(root).resolve()
    entries = manifest_entries(root)
    legacy = legacy_entries(root)
    all_entries = legacy + entries
    if len({e["path"] for e in all_entries}) != len(all_entries):
        raise FixtureError("Duplicate historical/legacy fixture destination")
    # Authenticate every source and every existing destination before writing.
    for entry in entries:
        source_bytes(root, entry)
    missing = []
    for entry in all_entries:
        target = target_path(root, entry["path"])
        if target.exists():
            if digest(read_bytes(target)) != entry["sha256"]:
                raise FixtureError("Existing fixture differs; refusing overwrite: " + entry["path"])
        else:
            missing.append(entry["path"])
    if check and missing:
        raise FixtureError("Historical fixtures not materialized: " + ", ".join(missing))
    if not check:
        materialize_export_inputs(root)
        for entry in entries:
            target = target_path(root, entry["path"])
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                value = source_bytes(root, entry)
                # Exclusive creation also protects against a concurrent writer.
                with target.open("xb") as stream:
                    stream.write(value)
    for entry in all_entries:
        if digest(read_bytes(target_path(root, entry["path"]))) != entry["sha256"]:
            raise FixtureError("Materialized fixture checksum mismatch: " + entry["path"])
    return {"legacy_inputs": len(legacy), "historical_inputs": len(entries),
            "verified_inputs": len(all_entries), "created": 0 if check else len(missing),
            "mode": "check" if check else "restore",
            "sha256": {entry["path"]: entry["sha256"] for entry in all_entries}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="Disposable checkout root (defaults to this script's repository)")
    parser.add_argument("--check", action="store_true", help="Verify all inputs without writing")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(restore(args.root, check=args.check), indent=2))
    except (FixtureError, AssertionError, KeyError, OSError) as error:
        print("Historical fixture setup failed: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
