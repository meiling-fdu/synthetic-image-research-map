#!/usr/bin/env python3
"""Audit key-paper coverage against canonical entities only."""

from __future__ import annotations
import csv
from pathlib import Path
try:
    from .canonical_authorship import load_canonical_dataset, normalize_title
except ImportError:
    from canonical_authorship import load_canonical_dataset, normalize_title

KEYS=Path("data/manual/key_papers.csv"); OUTPUT=Path("data/manual/key_paper_coverage_report.csv")
def main() -> int:
    with KEYS.open(encoding="utf-8-sig",newline="") as h: keys=list(csv.DictReader(h))
    data=load_canonical_dataset(); by_title={normalize_title(p["title"]):p for p in data["papers"]}
    fields=list(keys[0].keys() if keys else ["title","year"])+["canonical_paper_id","coverage_status","missing_stage","recommended_action"]
    rows=[]
    for row in keys:
        paper=by_title.get(normalize_title(row.get("title")))
        status=(paper or {}).get("coverage_status","missing_from_canonical_database")
        rows.append({**row,"canonical_paper_id":(paper or {}).get("paper_id",""),"coverage_status":status,"missing_stage":status,"recommended_action":"no_action" if status=="map_ready" else "review_canonical_record"})
    with OUTPUT.open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=fields,extrasaction="ignore",lineterminator="\n"); w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} canonical coverage rows to {OUTPUT}."); return 0
if __name__=="__main__": raise SystemExit(main())
