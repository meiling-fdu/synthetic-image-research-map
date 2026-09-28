#!/usr/bin/env python3
"""Read and verify the frozen 666-paper predecessor after its successor exists.

The reversible legacy-scope migration stores only its removed public records,
their original indexes, and hashes for every record that was not removed.  This
module reconstructs the predecessor in memory and verifies it against both the
migration snapshot and the original legacy-audit baseline manifest.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = (
    ROOT
    / "data/processed/legacy_scope_exclusion_migration_2026_09"
    / "predecessor_666_snapshot.json"
)
LEGACY_BASELINE_PATH = (
    ROOT / "data/processed/legacy_scope_cleanup_audit_2026_09/baseline_sha256.json"
)
PUBLIC_PAPERS_PATH = ROOT / "web/data/public_preview_papers.json"
PUBLIC_MAP_PATH = ROOT / "web/data/public_preview_map_data.json"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def row_sha256(row: Mapping[str, Any]) -> str:
    payload = json.dumps(
        dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return sha256_bytes(payload.encode("utf-8"))


def load_snapshot() -> dict[str, Any]:
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    baseline = json.loads(LEGACY_BASELINE_PATH.read_text(encoding="utf-8"))
    if snapshot.get("schema_version") != 1:
        raise AssertionError("unsupported 666-paper predecessor snapshot schema")
    if snapshot.get("counts") != baseline.get("corpus_counts"):
        raise AssertionError("predecessor counts do not match the legacy-audit baseline")
    if snapshot.get("tracked_pre_migration_sha256") != baseline.get(
        "tracked_baseline_sha256"
    ):
        raise AssertionError(
            "predecessor tracked-file manifest does not reproduce the legacy baseline"
        )
    expected_source_hashes = {
        "paper_exclusions.csv": baseline["tracked_baseline_sha256"][
            "data/curated/paper_exclusions.csv"
        ],
        "public_preview_papers.json": baseline["tracked_baseline_sha256"][
            "web/data/public_preview_papers.json"
        ],
        "public_preview_map_data.json": baseline["tracked_baseline_sha256"][
            "web/data/public_preview_map_data.json"
        ],
        "baseline_expectations.py": baseline["tracked_baseline_sha256"][
            "tests/baseline_expectations.py"
        ],
    }
    if snapshot.get("source_hashes") != expected_source_hashes:
        raise AssertionError(
            "predecessor source hashes do not match the legacy-audit baseline"
        )
    return snapshot


def _load_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        raise AssertionError(f"{path} must contain a records array")
    return payload


def _reconstructed_payload(dataset: str) -> dict[str, Any]:
    snapshot = load_snapshot()
    if dataset == "papers":
        path = PUBLIC_PAPERS_PATH
        metadata_key = "paper_metadata"
        targets_key = "target_public_papers"
        unrelated_key = "unrelated_public_record_sha256"
        source_key = "public_preview_papers.json"
    elif dataset == "map":
        path = PUBLIC_MAP_PATH
        metadata_key = "map_metadata"
        targets_key = "target_map_records"
        unrelated_key = "unrelated_map_record_sha256"
        source_key = "public_preview_map_data.json"
    else:
        raise ValueError(f"unknown predecessor dataset: {dataset}")

    payload = _load_payload(path)
    records = list(payload["records"])
    targets = snapshot[targets_key]
    target_hashes = {row_sha256(item["record"]) for item in targets}
    actual_unrelated = [
        row_sha256(row) for row in records if row_sha256(row) not in target_hashes
    ]
    if actual_unrelated != snapshot[unrelated_key]:
        raise AssertionError(
            f"current {dataset} records outside the migration delta changed"
        )

    present = {row_sha256(row) for row in records}
    for item in sorted(targets, key=lambda value: value["index"]):
        record_hash = row_sha256(item["record"])
        if record_hash not in present:
            records.insert(item["index"], item["record"])
            present.add(record_hash)

    reconstructed = dict(payload)
    reconstructed["metadata"] = snapshot[metadata_key]
    reconstructed["records"] = records
    text = json.dumps(reconstructed, ensure_ascii=False, indent=2) + "\n"
    actual_hash = sha256_bytes(text.encode("utf-8"))
    expected_hash = snapshot["source_hashes"][source_key]
    if actual_hash != expected_hash:
        raise AssertionError(
            f"reconstructed {source_key} hash {actual_hash} != {expected_hash}"
        )
    return reconstructed


def predecessor_public_records() -> list[dict[str, Any]]:
    return list(_reconstructed_payload("papers")["records"])


def predecessor_map_records() -> list[dict[str, Any]]:
    return list(_reconstructed_payload("map")["records"])


def predecessor_exclusion_bytes() -> bytes:
    snapshot = load_snapshot()
    value = base64.b64decode(snapshot["paper_exclusions_csv_base64"])
    actual_hash = sha256_bytes(value)
    expected_hash = snapshot["source_hashes"]["paper_exclusions.csv"]
    if actual_hash != expected_hash:
        raise AssertionError(
            f"reconstructed paper_exclusions.csv hash {actual_hash} != {expected_hash}"
        )
    return value


def predecessor_exclusion_rows() -> list[dict[str, str]]:
    text = predecessor_exclusion_bytes().decode("utf-8-sig")
    return [dict(row) for row in csv.DictReader(io.StringIO(text))]


def verify_predecessor() -> dict[str, object]:
    snapshot = load_snapshot()
    papers = predecessor_public_records()
    markers = predecessor_map_records()
    predecessor_exclusion_bytes()

    changed: list[str] = []
    missing: list[str] = []
    for relative, expected in snapshot["historical_artifact_sha256"].items():
        path = ROOT / relative
        if not path.is_file():
            missing.append(relative)
        elif sha256_bytes(path.read_bytes()) != expected:
            changed.append(relative)
    if changed:
        raise AssertionError(f"historical artifacts changed: {changed}")
    if missing:
        raise AssertionError(f"historical artifacts missing: {missing}")

    counts = {
        "public_papers": len(papers),
        "published_only": sum(
            row.get("publication_type") != "preprint" for row in papers
        ),
        "mapped_papers": sum(bool(row.get("has_map_location")) for row in papers),
        "map_markers": len(markers),
    }
    if counts != snapshot["counts"]:
        raise AssertionError(
            f"reconstructed predecessor counts {counts} != {snapshot['counts']}"
        )
    return {
        "manifest_entry_count": len(snapshot["tracked_pre_migration_sha256"]),
        "byte_verified_count": len(snapshot["historical_artifact_sha256"]) + 3,
        "byte_verified_match_count": len(snapshot["historical_artifact_sha256"]) + 3,
        "byte_verified_mismatch_count": 0,
        "historical_artifact_byte_verified_count": len(snapshot["historical_artifact_sha256"]),
        "reconstructed_byte_verified_count": 3,
        "verification_scope": "stored_hash_relationship_with_partial_byte_verification",
        "verification_method": (
            "Compare the complete frozen manifest with the legacy baseline manifest; "
            "hash every historical_artifact_sha256 file; reconstruct and hash public "
            "papers, map data, and exclusion registry bytes. Remaining manifest "
            "entries are not claimed as byte-verified."
        ),
        "changed": [],
        "missing": [],
        "corpus_counts": counts,
    }


def historical_verification_receipts() -> dict[str, object]:
    """Report current byte checks without reissuing frozen historical claims.

    Each layer's inventory is its original baseline manifest. Byte comparisons
    cover the retained layer artifacts locked by the immediate predecessor,
    which is a different, explicitly listed set of files.
    """
    predecessor = verify_predecessor()
    snapshot = load_snapshot()
    layers = (
        ("620-paper systematic audit", "systematic_literature_2026_09"),
        ("Tier 1 reconciliation", "systematic_tier1_2026_09"),
        ("636-paper Tier 2 policy analysis", "systematic_tier2_policy_2026_09"),
        ("636-paper Tier 2 policy application", "systematic_tier2_application_2026_09"),
        ("648-paper inclusion successor", "systematic_tier2_include_2026_09"),
        ("657-paper HIGH evidence successor", "systematic_tier2_high_priority_evidence_review_2026_09"),
        ("666-paper NORMAL evidence successor", "systematic_tier2_normal_priority_evidence_review_2026_09"),
        ("666-paper legacy-scope audit", "legacy_scope_cleanup_audit_2026_09"),
    )
    receipts = {}
    for label, directory in layers:
        manifest_path = ROOT / "data/processed" / directory / "baseline_sha256.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        inventory = manifest.get("tracked_baseline_sha256", manifest)
        tokens = (directory,)
        if directory == "legacy_scope_cleanup_audit_2026_09":
            tokens += ("legacy_scope_cleanup_2026_09",)
        checked = {
            path: digest for path, digest in snapshot["historical_artifact_sha256"].items()
            if any(token in path for token in tokens)
        }
        assert checked, label
        receipts[label] = {
            "result": "PASS",
            "manifest_entry_count": len(inventory),
            "byte_verified_count": len(checked),
            "byte_verified_match_count": len(checked),
            "byte_verified_mismatch_count": 0,
            "verification_scope": "stored_hash_relationship_with_partial_byte_verification",
            "verification_method": (
                "Hash retained layer artifacts against the frozen immediate-predecessor "
                "manifest. The original baseline inventory is not claimed fully "
                "byte-verified; artifact and inventory counts have different scopes."
            ),
            "manifest_path": manifest_path.relative_to(ROOT).as_posix(),
            "byte_verified_sha256": checked,
        }
        frozen_root = manifest_path.parent / "baseline"
        if directory == "systematic_literature_2026_09":
            frozen_root = ROOT / "data/processed/systematic_tier1_2026_09/baseline"
        if all((frozen_root / path).is_file() for path in inventory):
            compared = {}
            for path, expected in inventory.items():
                frozen = frozen_root / path
                actual = sha256_bytes(frozen.read_bytes())
                if actual != expected:
                    raise AssertionError(f"frozen baseline mismatch: {frozen}")
                compared[frozen.relative_to(ROOT).as_posix()] = actual
            receipts[label].update({
                "byte_verified_count": len(compared),
                "byte_verified_match_count": len(compared),
                "verification_scope": "fully_byte_verified",
                "verification_method": (
                    "Read and hash every original baseline manifest entry from its "
                    "frozen copy. Separately hash retained successor layer artifacts."
                ),
                "byte_verified_sha256": compared,
                "retained_layer_artifact_byte_verified_count": len(checked),
                "retained_layer_artifact_sha256": checked,
            })
    receipts["666-paper immediate pre-migration predecessor"] = {
        "result": "PASS", **predecessor,
    }
    return {"schema_version": 1, "layers": receipts}
