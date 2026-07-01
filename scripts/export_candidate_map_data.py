#!/usr/bin/env python3
"""Deprecated command name; delegates to the canonical public exporter."""

from __future__ import annotations

import sys

try:
    from .export_public_preview import main
except ImportError:
    from export_public_preview import main


if __name__ == "__main__":
    print(
        "NOTICE: candidate-map export is decommissioned; running canonical export.",
        file=sys.stderr,
    )
    raise SystemExit(main())
