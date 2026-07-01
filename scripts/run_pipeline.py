#!/usr/bin/env python3
"""Run the strict canonical-authorship publication pipeline."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

try:
    from .canonical_authorship import guard_no_legacy_runtime_references
except ImportError:
    from canonical_authorship import guard_no_legacy_runtime_references


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    guard_no_legacy_runtime_references()
    commands = [
        [sys.executable, "scripts/export_public_preview.py"],
        [sys.executable, "scripts/validate_public_preview.py"],
    ]
    for command in commands:
        print("$", " ".join(command))
        if args.dry_run:
            continue
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode:
            return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
