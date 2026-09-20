#!/usr/bin/env python3
"""Validate and render the bounded Tier 2 inclusion reconciliation."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from integrate_systematic_tier2_include import PAPERS, NEW, OUT, ROOT, paper_id
from paper_exclusions import active_exclusions, exclusions_with_curated_identities, matching_exclusion_rows, records_share_any_identity

CSV = ROOT / "data/manual/systematic_tier2_include_reconciliation_2026_09.csv"
REPORT = ROOT / "docs/systematic_tier2_include_reconciliation_2026_09.md"
FIELDS = ("candidate_id","title","policy_inclusion_rationale","reconciliation_outcome","paper_id","doi","arxiv_id","openalex_id","publication_status","version_relationship","primary_evidence","forensic_task","image_scope","research_type","affiliation_status","verified_affiliations","unresolved_fields","final_review_status","marker_count")
SUCCESSOR_BASELINE = ROOT / "data/processed/systematic_tier2_high_priority_evidence_review_2026_09/baseline"

def historical_state_path(relative):
    """Read the frozen 648-paper state once a successor layer is present."""
    candidate = SUCCESSOR_BASELINE / relative
    return candidate if candidate.exists() else ROOT / relative

def read_csv(path):
    with path.open(newline="") as h: return list(csv.DictReader(h))

def norm_title(value):
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()

def rows():
    proposals=json.loads((OUT/"planned_additions.json").read_text())["proposals"]
    queue={r["candidate_id"]:r for r in read_csv(ROOT/"data/processed/systematic_tier2_application_2026_09/queue_a_policy_include.csv")}
    public=json.loads(historical_state_path("web/data/public_preview_papers.json").read_text())["records"]
    markers=json.loads(historical_state_path("web/data/public_preview_map_data.json").read_text())["records"]
    result=[]
    for p in proposals:
        pid=p["paper_id"]; found=[r for r in public if r.get("paper_id")==pid]; assert len(found)==1
        new_names={x["canonical_name"] for x in NEW.values()}; pending=sorted({a["institution"] for a in p["verified_affiliations"] if a["institution"] in new_names})
        aff=" | ".join(f'{a["institution"]} [{"; ".join(a["authors"])}]' for a in p["verified_affiliations"])
        result.append({
            "candidate_id":p["cid"],"title":queue[p["cid"]]["title"],"policy_inclusion_rationale":queue[p["cid"]]["qualifying_synthetic_image_contribution"],
            "reconciliation_outcome":"MISSING_ADD","paper_id":pid,"doi":p["doi"],"arxiv_id":p["arxiv"],"openalex_id":p["oa"],
            "publication_status":p["ptype"],"version_relationship":p["version"],"primary_evidence":p["url"] + ((" | "+p["code"]) if p["code"] else ""),
            "forensic_task":p["tasks"],"image_scope":p["scopes"],"research_type":p["types"],
            "affiliation_status":"verified; location review pending" if pending else "verified",
            "verified_affiliations":aff,"unresolved_fields":("Coordinates pending for: "+"; ".join(pending)) if pending else "None",
            "final_review_status":"reviewed","marker_count":str(sum(m.get("paper_id")==pid for m in markers)),
        })
    return result

def diff_audit():
    names=("papers.csv","paper_taxonomy.csv","author_institution_mappings.csv","institutions.csv","institution_location_review.csv","institution_locations.csv","institution_aliases.csv","institution_hierarchy.csv","paper_exclusions.csv")
    out={}
    for name in names:
        old=read_csv(OUT/"baseline/data/curated"/name); new=read_csv(historical_state_path(f"data/curated/{name}"))
        changed=[i for i,r in enumerate(old) if i>=len(new) or r!=new[i]]; assert not changed,(name,changed[:10])
        out[name]={"existing_rows":len(old),"existing_rows_changed":0,"new_rows":len(new)-len(old)}
    hashes=json.loads((OUT/"baseline_sha256.json").read_text())
    frontend=[p for p in hashes if p.startswith("web/") and not p.startswith("web/data/")]
    out["frontend"]={"files_checked":len(frontend),"changed":sum(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=hashes[p] for p in frontend)}
    assert out["frontend"]["changed"]==0
    return out

def corpus_stats():
    papers=json.loads(historical_state_path("web/data/public_preview_papers.json").read_text())["records"]
    markers=json.loads(historical_state_path("web/data/public_preview_map_data.json").read_text())["records"]
    curated=read_csv(historical_state_path("data/curated/papers.csv"))
    exclusions=active_exclusions(exclusions_with_curated_identities(read_csv(historical_state_path("data/curated/paper_exclusions.csv")),curated))
    leaks=[p["title"] for p in papers if matching_exclusion_rows(p,exclusions)]; assert not leaks
    dup=[]
    for i,a in enumerate(papers):
        for b in papers[i+1:]:
            if records_share_any_identity(a,b): dup.append((a["title"],b["title"]))
    assert not dup,dup
    return {"public":len(papers),"published":sum(p.get("publication_type")!="preprint" for p in papers),"mapped":sum(bool(p.get("has_map_location")) for p in papers),"markers":len(markers),"duplicate_identity_pairs":dup,"active_exclusion_leaks":len(leaks)}

def identity_audit():
    baseline=json.loads((OUT/"baseline/web/data/public_preview_papers.json").read_text())["records"]
    exclusions=read_csv(OUT/"baseline/data/curated/paper_exclusions.csv")
    results=[]
    for p in PAPERS:
        strong=[]
        probe={"title":p["title"],"doi":p["doi"],"arxiv_id":p["arxiv"],"openalex_url":p["oa"]}
        for r in baseline:
            if records_share_any_identity(probe,r): strong.append(r.get("paper_id") or r.get("title"))
        ex=[r.get("exclusion_id") for r in exclusions if records_share_any_identity(probe,r)]
        fuzzy=sorted(((SequenceMatcher(None,norm_title(p["title"]),norm_title(r.get("title",""))).ratio(),r.get("title","")) for r in baseline),reverse=True)[:3]
        results.append({"candidate_id":p["cid"],"doi":p["doi"],"arxiv_id":p["arxiv"],"openalex_url":p["oa"],"strong_matches":strong,"active_exclusion_matches":ex,"top_bounded_fuzzy_title_matches":[{"score":round(s,4),"title":t} for s,t in fuzzy],"authors_year_venue_review":"No matching work established; author/year/venue and method/acronym checks reviewed manually.","outcome":"MISSING_ADD"})
        assert not strong and not ex
    return results

def render(rs,stats,diffs):
    counts=Counter(r["reconciliation_outcome"] for r in rs)
    lines=["# Tier 2 inclusion reconciliation — September 2026","","This pass reconciles only the 12 decision-ready `POLICY_INCLUDE` candidates. The 32 evidence-required candidates, 171 policy exclusions, Tier 3, and legacy-scope diagnostics remain untouched.","","The canonical decisions are in [systematic_tier2_include_reconciliation_2026_09.csv](../data/manual/systematic_tier2_include_reconciliation_2026_09.csv). Counts and tables below are generated from that file and the current authoritative exports.","","## Outcomes","",json.dumps(dict(sorted(counts.items())),sort_keys=True),"",f"Public papers: 636 → {stats['public']}; published-only: 528 → {stats['published']}; mapped papers: 623 → {stats['mapped']}; markers: {stats['markers']}.","","| Title | Outcome / ID | Publication | Task | Scope | Research type | Affiliations | Markers | Remaining issue |","|---|---|---|---|---|---|---|---:|---|"]
    for r in rs:
        vals=[r["title"],r["reconciliation_outcome"]+" / "+r["paper_id"],r["publication_status"],r["forensic_task"],r["image_scope"],r["research_type"],r["affiliation_status"],r["marker_count"],r["unresolved_fields"]]
        lines.append("| "+" | ".join(v.replace("|","\\|") for v in vals)+" |")
    lines += ["","## Scope rechecks","","- **STD-FD:** in scope. Its temporal axis is diffusion reconstruction time; evaluation is still-image AIGC detection.","- **Untraceable DeepFakes:** in scope. It removes naturally occurring generator traces used by passive attribution systems; it does not depend on an injected watermark and is not face-only.","- **NeuroRenderedFake:** in scope. Its benchmark covers neural rendering plus GAN and diffusion imagery, beyond conventional face/video deepfakes.","- **UniShield:** in scope. The relevant AIGC endpoint is passive image detection and localization, not content protection or proactive authentication.","- **ImageTrust:** in scope. It is an AI-generated-image detector with recompression robustness and calibrated uncertainty, not a generic trust score.","- **Scalable Black-Box Model Attribution for Images:** in scope. It infers the source generator from the image in a strict black-box setting without an embedded signature.","","## Identity, versions, and exclusions","","All 12 candidates were checked against the pre-task 636-paper export and the active exclusion registry using DOI, arXiv, OpenAlex, normalized title, author/year/venue, method/acronym, alternate-version evidence, and bounded fuzzy titles. All resolve to `MISSING_ADD`; no active exclusion matched. [Identity checks](../data/processed/systematic_tier2_include_2026_09/identity_checks.json) retain the compared identifiers and closest title candidates.","","TGIF2 is retained as the expanded dataset/benchmark rather than conflated with TGIF. The IEEE TMM vulnerabilities article, CVPR IFA-Net paper, and current arXiv records are represented once under their canonical versions. No workshop/final or preprint/publication pair was inserted twice.","","## Strict pre-task diff","","| File | Existing rows changed | Added rows |","|---|---:|---:|"]
    for n,d in diffs.items():
        if n!="frontend": lines.append(f"| {n} | {d['existing_rows_changed']} | {d['new_rows']} |")
    lines += ["",f"New institutions: {'; '.join(NEW)}.","","No institution aliases, confirmed locations, or hierarchy relationships were added. Nine pending location-review rows preserve primary affiliation evidence without inventing coordinates. Markerless papers remain visible in the paper list.","","## Corpus impact","",f"Twelve papers were added. By year: {dict(sorted(Counter(r['year'] for r in PAPERS).items()))}. By venue: {dict(sorted(Counter(r['venue'] for r in PAPERS).items()))}. By task: {dict(sorted(Counter(x for r in rs for x in r['forensic_task'].split(';')).items()))}. By image scope: {dict(sorted(Counter(x for r in rs for x in r['image_scope'].split(';')).items()))}. By research type: {dict(sorted(Counter(x for r in rs for x in r['research_type'].split(';')).items()))}.","","## Validation","","The public exporter preserved the previous corpus while integrating reviewed curated rows. The final export has no active-exclusion leak or duplicate strong identity. Focused tests, schema validators, public-preview validation, full-suite output, and reproducibility checks are retained in `data/processed/systematic_tier2_include_2026_09/`. Existing authoritative rows and frontend assets are unchanged. No commit or push was performed.",""]
    return "\n".join(lines)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--emit-csv",action="store_true"); ap.add_argument("--check",action="store_true"); args=ap.parse_args()
    expected=rows()
    if args.emit_csv:
        w=csv.DictWriter(sys.stdout,fieldnames=FIELDS,lineterminator="\n"); w.writeheader(); w.writerows(expected); return
    actual=read_csv(CSV); assert actual==expected,"Canonical Tier 2 reconciliation CSV differs from current reviewed/exported state."
    diffs=diff_audit(); stats=corpus_stats(); identity=identity_audit(); rendered=render(actual,stats,diffs)
    OUT.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(identity,indent=2,ensure_ascii=False)+"\n"; validation=json.dumps({"outcomes":dict(Counter(r["reconciliation_outcome"] for r in actual)),"corpus":stats,"diff":diffs},indent=2,sort_keys=True)+"\n"
    if args.check:
        assert REPORT.read_text()==rendered and (OUT/"identity_checks.json").read_text()==payload and (OUT/"validation_data.json").read_text()==validation
    else:
        REPORT.write_text(rendered); (OUT/"identity_checks.json").write_text(payload); (OUT/"validation_data.json").write_text(validation)
    print(json.dumps(stats,sort_keys=True))

if __name__=="__main__": main()
