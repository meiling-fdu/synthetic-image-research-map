#!/usr/bin/env python3
"""Diagnose canonical key-paper export readiness without candidate artifacts."""

from __future__ import annotations
import csv
from pathlib import Path
try:
    from .canonical_authorship import load_canonical_dataset
except ImportError:
    from canonical_authorship import load_canonical_dataset

OUTPUT=Path("data/manual/key_paper_export_diagnostics.csv")
COLUMNS=("title","year","normalized_title","key_paper_status","canonical_paper_id","openalex_url","doi","affiliation_record_status","coordinate_status","export_status","skip_reason","recommended_next_action","notes")
def main() -> int:
    data=load_canonical_dataset(); rows=[]
    for paper in data["papers"]:
        if paper["coverage_status"]=="map_ready": continue
        rows.append({"title":paper["title"],"year":paper["year"],"normalized_title":paper["title"].casefold(),"key_paper_status":"canonical","canonical_paper_id":paper["paper_id"],"openalex_url":paper.get("openalex_url",""),"doi":paper.get("doi",""),"affiliation_record_status":"missing" if paper["missing_affiliation"] else "canonical","coordinate_status":"missing" if paper["missing_coordinates"] else "known","export_status":"paper_only","skip_reason":paper["coverage_status"],"recommended_next_action":"review_canonical_record","notes":""})
    with OUTPUT.open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=COLUMNS,lineterminator="\n"); w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} canonical export diagnostics to {OUTPUT}."); return 0
if __name__=="__main__": raise SystemExit(main())
