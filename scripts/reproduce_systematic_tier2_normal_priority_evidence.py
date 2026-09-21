#!/usr/bin/env python3
"""Regenerate the NORMAL-evidence successor twice and require byte identity."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/processed/systematic_tier2_normal_priority_evidence_review_2026_09"
GENERATED_PATHS = (
    "data/curated/papers.csv",
    "data/curated/paper_taxonomy.csv",
    "data/curated/author_institution_mappings.csv",
    "data/curated/institutions.csv",
    "data/curated/institution_location_review.csv",
    "data/manual/systematic_tier2_normal_priority_evidence_review_2026_09.csv",
    "docs/systematic_tier2_normal_priority_evidence_review_2026_09.md",
    "data/processed/systematic_tier2_normal_priority_evidence_review_2026_09/planned_additions.json",
    "data/processed/systematic_tier2_normal_priority_evidence_review_2026_09/insertion.json",
    "data/processed/systematic_tier2_normal_priority_evidence_review_2026_09/identity_checks.json",
    "data/processed/systematic_tier2_normal_priority_evidence_review_2026_09/diff_audit.json",
    "data/processed/systematic_tier2_normal_priority_evidence_review_2026_09/validation_data.json",
    "web/data/public_preview_papers.json",
    "web/data/public_preview_map_data.json",
    "data/manual/key_paper_coverage_report.csv",
    "docs/key_paper_coverage_report.md",
    "data/manual/missing_author_mappings_report.csv",
    "docs/missing_author_mappings_report.md",
    "docs/public_preview_report.md",
)
PROTECTED_PATHS = (
    "data/processed/systematic_tier2_normal_priority_evidence_review_2026_09/evidence_lock.json",
    "data/processed/systematic_tier2_normal_priority_evidence_review_2026_09/identity_lock.json",
    "data/processed/systematic_tier2_normal_priority_evidence_review_2026_09/preinsertion_identity_checks.json",
    "data/processed/systematic_tier2_normal_priority_evidence_review_2026_09/baseline_sha256.json",
    "data/processed/institution_type_audit.csv",
    "data/curated/institution_locations.csv",
    "data/curated/institution_aliases.csv",
    "data/curated/institution_hierarchy.csv",
    "data/curated/paper_exclusions.csv",
    "data/curated/venue_aliases.csv",
)


def hashes(paths: tuple[str, ...]) -> dict[str, str]:
    return {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def load_records(path: Path) -> list[dict[str, object]]:
    return json.loads(path.read_text(encoding="utf-8"))["records"]


def assert_frozen_predecessor() -> None:
    assert (OUT / "insertion.json").exists(), "The reviewed insertion receipt is required."
    baseline = OUT / "baseline"
    assert len(load_records(baseline / "web/data/public_preview_papers.json")) == 657
    assert len(load_records(baseline / "web/data/public_preview_map_data.json")) == 1494


def run_round() -> str:
    commands = (
        ("integrate_systematic_tier2_normal_priority_evidence.py",),
        (
            "refresh_public_preview.py",
            "--skip-search",
            "--user-agent",
            "SyntheticImageResearchMap-NormalPriorityEvidence/1.0",
        ),
        ("report_systematic_tier2_normal_priority_evidence.py", "--write"),
        ("report_systematic_tier2_normal_priority_evidence.py", "--check"),
    )
    chunks: list[str] = []
    environment = dict(os.environ)
    environment["PYTHONPYCACHEPREFIX"] = "/tmp/sirm-pycache"
    for command in commands:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / command[0]), *command[1:]],
            cwd=ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        chunks.append("$ " + " ".join(command))
        chunks.append(result.stdout.rstrip())
        if result.stderr:
            chunks.append(result.stderr.rstrip())
    return "\n".join(chunks) + "\n"


def main() -> None:
    assert_frozen_predecessor()
    initial = hashes(GENERATED_PATHS)
    protected_initial = hashes(PROTECTED_PATHS)
    first_log = run_round()
    first = hashes(GENERATED_PATHS)
    assert hashes(PROTECTED_PATHS) == protected_initial
    second_log = run_round()
    second = hashes(GENERATED_PATHS)
    protected_final = hashes(PROTECTED_PATHS)
    result = {
        "byte_identical": first == second,
        "matches_pre_run": initial == first,
        "changed_after_first": sorted(
            path for path in GENERATED_PATHS if initial[path] != first[path]
        ),
        "changed_after_second": sorted(
            path for path in GENERATED_PATHS if first[path] != second[path]
        ),
        "generated_paths_checked": len(GENERATED_PATHS),
        "protected_paths_checked": len(PROTECTED_PATHS),
        "protected_inputs_unchanged": protected_initial == protected_final,
        "rounds": 2,
        "sha256": second,
        "protected_sha256": protected_final,
    }
    (OUT / "reproduction_log.txt").write_text(
        "ROUND 1\n" + first_log + "\nROUND 2\n" + second_log,
        encoding="utf-8",
    )
    (OUT / "reproducibility.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    assert result["byte_identical"], result
    assert result["matches_pre_run"], result
    assert result["protected_inputs_unchanged"], result
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
