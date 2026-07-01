#!/usr/bin/env python3
"""List canonical institutions that still need reviewed coordinates."""

from __future__ import annotations
import csv
from pathlib import Path
try:
    from .canonical_authorship import load_canonical_dataset
except ImportError:
    from canonical_authorship import load_canonical_dataset

OUTPUT=Path("data/manual/key_paper_coordinate_candidates.csv")
COLUMNS=("title","year","normalized_title","openalex_url","doi","author","author_position","institution","city","region","country","country_code","current_latitude","current_longitude","candidate_latitude","candidate_longitude","candidate_source","candidate_source_detail","candidate_confidence","coordinate_status","apply_status","risk_flags","notes")

def main() -> int:
    data=load_canonical_dataset(); rows=[]
    marker_ids={(m["paper_id"],m["institution_id"]) for m in data["markers"]}
    for paper in data["papers"]:
        for institution in paper["canonical_authorship"]["institutions"]:
            if institution["institution_id"]=="institution:unresolved" or (paper["paper_id"],institution["institution_id"]) in marker_ids: continue
            rows.append({"title":paper["title"],"year":paper["year"],"normalized_title":paper["title"].casefold(),"openalex_url":paper.get("openalex_url",""),"doi":paper.get("doi",""),"institution":institution["canonical_name"],"coordinate_status":"missing","apply_status":"needs_manual_review","risk_flags":"canonical_location_missing","notes":"Canonical institution has no reviewed coordinate."})
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    with OUTPUT.open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=COLUMNS,extrasaction="ignore",lineterminator="\n"); w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} canonical coordinate candidates to {OUTPUT}."); return 0
if __name__=="__main__": raise SystemExit(main())
