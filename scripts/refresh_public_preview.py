#!/usr/bin/env python3
"""Compatibility command for the strict canonical publication pipeline."""

from __future__ import annotations

try:
    from .run_pipeline import main
except ImportError:
    from run_pipeline import main


if __name__ == "__main__":
    raise SystemExit(main())
