#!/usr/bin/env python3
"""Report review risks directly from canonical authorship entities."""

from __future__ import annotations
import csv
from pathlib import Path
try:
    from .canonical_authorship import load_canonical_dataset
except ImportError:
    from canonical_authorship import load_canonical_dataset

OUTPUT = Path("data/manual/high_risk_marker_review.csv")
COLUMNS = ("priority","review_type","title","year","doi","openalex_url","institution","institution_authors","city","region","country","country_code","lat","lon","source_database","metadata_source","publication_type","task","subtask","needs_review","resolution_confidence","resolution_method","resolution_notes","current_public_preview_status","recommended_action","review_note")

def main() -> int:
    data = load_canonical_dataset()
    rows = []
    for paper in data["papers"]:
        unresolved = [
            item for item in paper["canonical_authorship"]["institutions"]
            if item["institution_id"] == "institution:unresolved"
        ]
        if not paper["needs_review"] and not unresolved:
            continue
        rows.append({
            "priority":"P1","review_type":"canonical_authorship_review",
            "title":paper["title"],"year":paper["year"],"doi":paper.get("doi",""),
            "openalex_url":paper.get("openalex_url",""),
            "institution":"; ".join(item["canonical_name"] for item in unresolved),
            "source_database":"; ".join(paper.get("provenance_sources",[])),
            "task":paper.get("task",""),"subtask":paper.get("subtask",""),
            "needs_review":"true","current_public_preview_status":paper["coverage_status"],
            "recommended_action":"replace_author_institution_mapping","review_note":"",
        })
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=COLUMNS,extrasaction="ignore",lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    print(f"Wrote {len(rows)} canonical risk rows to {OUTPUT}.")
    return 0
if __name__ == "__main__": raise SystemExit(main())
