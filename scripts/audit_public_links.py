#!/usr/bin/env python3
"""Audit curated arXiv DOI records that also carry a distinct formal URL."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Mapping

try:
    from .paper_links import canonical_url, is_arxiv_doi, normalize_doi, resolve_public_links
except ImportError:
    from paper_links import canonical_url, is_arxiv_doi, normalize_doi, resolve_public_links


ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "data/curated/papers.csv"
REPORT = ROOT / "docs/public_link_conflict_audit.csv"
FIELDS = (
    "paper_id",
    "title",
    "arxiv_id",
    "stored_doi",
    "paper_url",
    "resolved_formal_doi",
    "resolved_formal_url",
    "status",
    "reason",
)


def audit_row(row: Mapping[str, Any]) -> dict[str, str] | None:
    stored_doi = str(row.get("doi") or "").strip()
    paper_url = str(row.get("paper_url") or "").strip()
    links = resolve_public_links(row)
    if not is_arxiv_doi(stored_doi):
        return None
    target = canonical_url(paper_url)
    if not paper_url or target.startswith(("arxiv:", "openalex:")):
        return None
    formal_doi = normalize_doi(paper_url)
    status = "confident_formal_doi" if formal_doi and not is_arxiv_doi(formal_doi) else "needs_review"
    reason = (
        "Distinct formal DOI is explicit in paper_url; safe to migrate."
        if status == "confident_formal_doi"
        else "Distinct publisher URL exists, but no formal DOI is explicit in curated fields."
    )
    return {
        "paper_id": str(row.get("paper_id") or ""),
        "title": str(row.get("title") or ""),
        "arxiv_id": links["arxiv_id"],
        "stored_doi": stored_doi,
        "paper_url": paper_url,
        "resolved_formal_doi": formal_doi,
        "resolved_formal_url": links["formal_url"],
        "status": status,
        "reason": reason,
    }


def main() -> int:
    with PAPERS.open(encoding="utf-8-sig", newline="") as handle:
        audited = [
            result
            for row in csv.DictReader(handle)
            if (result := audit_row(row)) is not None
        ]
    with REPORT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(audited)
    print(f"Wrote {len(audited)} unresolved conflicts to {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
