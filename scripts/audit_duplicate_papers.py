#!/usr/bin/env python3
"""Report exact curated-paper identity collisions without modifying data."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

try:
    from .curated_papers import read_curated_papers
    from .validate_curated_database import validate_paper_duplicates
except ImportError:  # pragma: no cover
    from curated_papers import read_curated_papers
    from validate_curated_database import validate_paper_duplicates


DEFAULT_PAPERS = Path("data/curated/papers.csv")


def audit(path: Path = DEFAULT_PAPERS) -> list:
    issues = []
    return validate_paper_duplicates(read_curated_papers(path), issues)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--papers", type=Path, default=DEFAULT_PAPERS)
    args = parser.parse_args(argv)
    duplicates = audit(args.papers)
    for duplicate in duplicates:
        print(
            f"DUPLICATE: {duplicate.field} rows "
            f"{', '.join(map(str, duplicate.row_numbers))}: {duplicate.value}"
        )
    print(f"Duplicate curated-paper identities: {len(duplicates)}")
    return 1 if duplicates else 0


if __name__ == "__main__":
    raise SystemExit(main())
