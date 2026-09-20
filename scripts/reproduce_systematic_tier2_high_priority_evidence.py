#!/usr/bin/env python3
"""Regenerate the HIGH-evidence successor twice and require byte identity."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/processed/systematic_tier2_high_priority_evidence_review_2026_09"
PATHS = (
    "data/curated/papers.csv",
    "data/curated/paper_taxonomy.csv",
    "data/curated/author_institution_mappings.csv",
    "data/curated/institutions.csv",
    "data/curated/institution_location_review.csv",
    "data/manual/systematic_tier2_high_priority_evidence_review_2026_09.csv",
    "docs/systematic_tier2_high_priority_evidence_review_2026_09.md",
    "data/processed/systematic_tier2_high_priority_evidence_review_2026_09/planned_additions.json",
    "data/processed/systematic_tier2_high_priority_evidence_review_2026_09/insertion.json",
    "data/processed/systematic_tier2_high_priority_evidence_review_2026_09/identity_checks.json",
    "data/processed/systematic_tier2_high_priority_evidence_review_2026_09/diff_audit.json",
    "data/processed/systematic_tier2_high_priority_evidence_review_2026_09/validation_data.json",
    "web/data/public_preview_papers.json",
    "web/data/public_preview_map_data.json",
    "data/manual/key_paper_coverage_report.csv",
    "docs/key_paper_coverage_report.md",
    "data/manual/missing_author_mappings_report.csv",
    "docs/missing_author_mappings_report.md",
    "docs/public_preview_report.md",
    "data/processed/institution_type_audit.csv",
)


def hashes() -> dict[str, str]:
    return {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in PATHS
    }


def run_round() -> str:
    commands = (
        ("integrate_systematic_tier2_high_priority_evidence.py",),
        (
            "refresh_public_preview.py",
            "--skip-search",
            "--user-agent",
            "SyntheticImageResearchMap-HighPriorityEvidence/1.0",
        ),
        ("report_systematic_tier2_high_priority_evidence.py", "--write"),
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
    initial = hashes()
    first_log = run_round()
    first = hashes()
    second_log = run_round()
    second = hashes()
    result = {
        "byte_identical": initial == first == second,
        "changed_after_first": sorted(path for path in PATHS if initial[path] != first[path]),
        "changed_after_second": sorted(path for path in PATHS if first[path] != second[path]),
        "paths_checked": len(PATHS),
        "rounds": 2,
        "sha256": second,
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
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
