#!/usr/bin/env python3
"""Compatibility entry point for the institution English-name migration."""

from __future__ import annotations

import sys

try:
    from .migrate_institution_english_names import *  # noqa: F401,F403
    from .migrate_institution_english_names import main
except ImportError:
    from migrate_institution_english_names import *  # noqa: F401,F403
    from migrate_institution_english_names import main


if __name__ == "__main__":
    arguments = [
        "--dry-run" if argument == "--check" else
        "--apply" if argument == "--apply-high-confidence" else
        argument
        for argument in sys.argv[1:]
    ]
    raise SystemExit(main(arguments))
