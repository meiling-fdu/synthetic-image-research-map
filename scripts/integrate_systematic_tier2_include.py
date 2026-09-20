#!/usr/bin/env python3
"""Append the twelve primary-source-reviewed Tier 2 inclusion records."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import shutil
from pathlib import Path

from curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS, INSTITUTION_COLUMNS,
    INSTITUTION_LOCATION_REVIEW_COLUMNS, PAPERS_COLUMNS, PAPER_TAXONOMY_COLUMNS,
)
from venues import canonicalize_record
from title_normalization import canonical_paper_title

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/processed/systematic_tier2_include_2026_09"
QUEUE = ROOT / "data/processed/systematic_tier2_application_2026_09/queue_a_policy_include.csv"
NOW = "2026-09-19T00:00:00Z"

def hid(prefix: str, value: str, n: int) -> str:
    return prefix + hashlib.sha256(value.encode()).hexdigest()[:n]

def paper_id(candidate_id: str) -> str:
    return hid("curated:", "systematic-tier2-include:" + candidate_id, 20)

def new_inst(name: str, kind: str, abbreviation: str = "") -> dict:
    iid = hid("institution:", "tier2-include:" + name, 16)
    return dict(institution_id=iid, canonical_name=name, abbreviation=abbreviation,
                institution_type=kind, institution_status="active", parent_institution_id="",
                public_display="self", created_at=NOW, updated_at=NOW,
                created_by="primary-source-curation")

NEW = {i["canonical_name"]: i for i in [
    new_inst("Ghent University", "university"),
    new_inst("imec", "research_unit", "imec"),
    new_inst("BBC Research & Development", "research_unit", "BBC R&D"),
    new_inst("Lenovo Research", "company"),
    new_inst("Reality Defender", "company"),
    new_inst("Wuhan University of Technology", "university"),
    new_inst("West University of Timișoara", "university", "UVT"),
    new_inst("Chongqing University", "university", "CQU"),
    new_inst("Rochester Institute of Technology", "university", "RIT"),
]}

EXISTING = {
 "Zhejiang University":"institution:e433baf78e80004b", "Zhejiang University of Technology":"institution:9b91aedca1273b56",
 "Hefei University of Technology":"institution:f6342fd457763517", "Hangzhou High-Tech Zone (Binjiang) Institute of Blockchain and Data Security":"institution:91e76fe32279c58d",
 "Centre for Research and Technology Hellas":"institution:f841aa8a7a0d29aa", "University of Science and Technology of China":"institution:e721b03b6f6c172d",
 "Great Bay University":"institution:c33f0550d2263d47", "Beihang University":"institution:f336b3005794930b",
 "University of Bologna":"institution:e73ae6a6d6ff3735", "Mohamed bin Zayed University of Artificial Intelligence":"institution:f04b96a9716ab2f4",
 "University of Oxford":"institution:87d9a45b3389372f", "Institute of Artificial Intelligence, Hefei Comprehensive National Science Center":"institution:db049bef3a2d25e0",
 "Michigan State University":"institution:cd887bf808040e61", "Tel Aviv University":"institution:7df4a1601453f806",
 "Carnegie Mellon University":"institution:c5235efb76365de2", "The Hong Kong Polytechnic University":"institution:31f980eaa403801a",
 "Peking University":"institution:46e4866d3b2954ab", "South China University of Technology":"institution:3e9b289ae248f660",
 "Qilu University of Technology":"institution:77fb2ba62b721cd6",
}

def aff(name, authors, raw): return {"institution":name,"authors":authors,"raw":raw}

PAPERS = [
 dict(cid="audit:032ad7d6b71836a2", title="STD-FD: Spatio-Temporal Distribution Fitting Deviation for AIGC Forgery Identification", year="2025", authors=["Hengrui Lou","Zunlei Feng","Jinsong Geng","Erteng Liu","Jie Lei","Lechao Cheng","Jie Song","Mingli Song","Yijun Bei"], venue="Proceedings of the 42nd International Conference on Machine Learning", ptype="conference", doi="", arxiv="", oa="", url="https://proceedings.mlr.press/v267/lou25a.html", code="", tasks="detection", scopes="fully_generated", types="method;analysis_study", affiliations=[aff("Zhejiang University",["Hengrui Lou","Zunlei Feng","Erteng Liu","Jie Song","Mingli Song","Yijun Bei"],"State Key Laboratory of Blockchain and Data Security, Zhejiang University"),aff("Zhejiang University",["Zunlei Feng","Jinsong Geng","Jie Song","Yijun Bei"],"School of Software Technology, Zhejiang University"),aff("Zhejiang University of Technology",["Jie Lei"],"College of Computer Science, Zhejiang University of Technology"),aff("Hefei University of Technology",["Lechao Cheng"],"School of Computer Science and Information Engineering, Hefei University of Technology"),aff("Hangzhou High-Tech Zone (Binjiang) Institute of Blockchain and Data Security",["Mingli Song"],"Hangzhou High-Tech Zone (Binjiang) Institute of Blockchain and Data Security")], version="One primary ICML 2025 work; temporal denotes diffusion reconstruction steps, not video."),
 dict(cid="audit:07194f58b4540acc", title="TGIF2: extended text-guided inpainting forgery dataset and benchmark", year="2026", authors=["Hannes Mareen","Dimitrios Karageorgiou","Paschalis Giakoumoglou","Peter Lambert","Symeon Papadopoulos","Glenn Van Wallendael"], venue="Journal on Information Security", ptype="journal", doi="10.1186/s13635-026-00235-9", arxiv="", oa="https://openalex.org/W7153215624", url="https://doi.org/10.1186/s13635-026-00235-9", code="https://github.com/IDLabMedia/tgif-dataset", tasks="detection;localization", scopes="generative_editing", types="dataset;benchmark;analysis_study", affiliations=[aff("Ghent University",["Hannes Mareen","Peter Lambert","Glenn Van Wallendael"],"IDLab, Ghent University – imec, Gent, Belgium"),aff("imec",["Hannes Mareen","Peter Lambert","Glenn Van Wallendael"],"IDLab, Ghent University – imec, Gent, Belgium"),aff("Centre for Research and Technology Hellas",["Dimitrios Karageorgiou","Paschalis Giakoumoglou","Symeon Papadopoulos"],"Information Technologies Institute, CERTH, Thessaloniki, Greece")], version="Journal extension of TGIF with FLUX.1 edits, random masks and expanded benchmarking; represented as the distinct TGIF2 work."),
 dict(cid="audit:2ec9b9251586d3bb", title="Vulnerabilities in AI-generated Image Detection: The Challenge of Adversarial Attacks", year="2026", authors=["Yunfeng Diao","Naixin Zhai","Changtao Miao","Zitong Yu","Xingxing Wei","Xun Yang","Meng Wang"], venue="IEEE Transactions on Multimedia", ptype="journal", doi="10.1109/TMM.2026.3682154", arxiv="2407.20836", oa="https://openalex.org/W4401203256", url="https://doi.org/10.1109/TMM.2026.3682154", code="https://github.com/onotoa/fpba", tasks="detection", scopes="fully_generated", types="method;analysis_study", affiliations=[aff("Hefei University of Technology",["Yunfeng Diao","Meng Wang"],"Hefei University of Technology; Intelligent Interconnected Systems Laboratory of Anhui Province (Hefei University of Technology)"),aff("University of Science and Technology of China",["Naixin Zhai","Changtao Miao","Xun Yang"],"University of Science and Technology of China, Hefei, China"),aff("Great Bay University",["Zitong Yu"],"Great Bay University, Dongguan, China"),aff("Beihang University",["Xingxing Wei"],"Beihang University, Beijing, China")], version="arXiv 2407.20836 is the preprint of the final IEEE TMM article; only the final article is represented."),
 dict(cid="audit:3e3ef129a9a7d54a", title="Towards Reliable Identification of Diffusion-based Image Manipulations", year="2025", authors=["Alex Costanzino","Woody Bayliss","Juil Sock","Marc Gorriz Blanch","Danijela Horak","Ivan Laptev","Philip H. S. Torr","Fabio Pizzati"], venue="Advances in Neural Information Processing Systems", ptype="conference", doi="10.52202/085713-1270", arxiv="", oa="https://openalex.org/W4417095836", url="https://proceedings.neurips.cc/paper_files/paper/2025/hash/36721d1209a059dcb7a090dd543f34c4-Abstract-Conference.html", code="https://alex-costanzino.github.io/radar/", tasks="detection;localization", scopes="generative_editing", types="method;dataset;benchmark", affiliations=[aff("University of Bologna",["Alex Costanzino"],"University of Bologna"),aff("BBC Research & Development",["Woody Bayliss","Juil Sock","Marc Gorriz Blanch","Danijela Horak"],"BBC R&D"),aff("Mohamed bin Zayed University of Artificial Intelligence",["Ivan Laptev","Fabio Pizzati"],"MBZUAI"),aff("University of Oxford",["Philip H. S. Torr"],"University of Oxford")], version="One NeurIPS 2025 work; no separate workshop or journal version was established."),
 dict(cid="audit:5413d2706f713d11", title="Untraceable DeepFakes via Traceable Fingerprint Elimination", year="2026", authors=["Jiewei Lai","Lan Zhang","Chen Tang","Pengcheng Sun","Xinming Wang","Yunhao Wang"], venue="International Conference on Learning Representations", ptype="conference", doi="", arxiv="", oa="", url="https://proceedings.iclr.cc/paper_files/paper/2026/hash/8e8399e5e7aed601c9f135f40be26564-Abstract-Conference.html", code="", tasks="source_attribution", scopes="fully_generated", types="method;analysis_study", affiliations=[aff("University of Science and Technology of China",["Jiewei Lai","Lan Zhang","Chen Tang","Pengcheng Sun","Xinming Wang"],"University of Science and Technology of China"),aff("Institute of Artificial Intelligence, Hefei Comprehensive National Science Center",["Lan Zhang"],"Institute of Artificial Intelligence, Hefei Comprehensive National Science Center"),aff("Lenovo Research",["Yunhao Wang"],"Lenovo Research")], version="One ICLR 2026 work attacking naturally occurring generator traces used by passive attribution; no embedded watermark is required."),
 dict(cid="audit:5a3a0232762bb033", title="PolyJuice Makes It Real: Black-Box, Universal Red Teaming for Synthetic Image Detectors", year="2025", authors=["Sepehr Dehdashtian","Mashrur M. Morshed","Jacob H. Seidman","Gaurav Bharaj","Vishnu Naresh Boddeti"], venue="Advances in Neural Information Processing Systems", ptype="conference", doi="10.52202/085713-4260", arxiv="", oa="https://openalex.org/W4414697949", url="https://proceedings.neurips.cc/paper_files/paper/2025/hash/b9b228d28770dc2a18922de5cd49f1d9-Abstract-Conference.html", code="https://sepehrdehdashtian.github.io/Papers/PolyJuice", tasks="detection", scopes="fully_generated", types="method;analysis_study", affiliations=[aff("Michigan State University",["Sepehr Dehdashtian","Mashrur M. Morshed","Vishnu Naresh Boddeti"],"Michigan State University"),aff("Reality Defender",["Jacob H. Seidman","Gaurav Bharaj"],"Reality Defender")], version="One NeurIPS 2025 black-box red-teaming method and detector-robustness analysis."),
 dict(cid="audit:6bf3721fdb65fc44", title="Detecting AI-Generated Forgeries via Iterative Manifold Deviation Amplification", year="2026", authors=["Jiangling Zhang","Shuxuan Gao","Bofan Liu","Siqiang Feng","Jirui Huang","Yaxiong Chen","Ziyu Chen"], venue="Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition", ptype="conference", doi="", arxiv="2602.18842", oa="https://openalex.org/W7131399153", url="https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_Detecting_AI-Generated_Forgeries_via_Iterative_Manifold_Deviation_Amplification_CVPR_2026_paper.html", code="", tasks="detection;localization", scopes="generative_editing", types="method", affiliations=[aff("Wuhan University of Technology",["Jiangling Zhang","Shuxuan Gao","Bofan Liu","Siqiang Feng","Jirui Huang","Yaxiong Chen","Ziyu Chen"],"Wuhan University of Technology")], version="arXiv 2602.18842 and the CVPR 2026 proceedings paper are one work; the proceedings representation is canonical."),
 dict(cid="audit:80dc647f134b129b", title="Scalable Black-Box Model Attribution for Images", year="2026", authors=["Asaf Livne","Amir Jevnisek","Shai Avidan"], venue="arXiv", ptype="preprint", doi="10.48550/arXiv.2608.15652", arxiv="2608.15652", oa="https://openalex.org/W7203704211", url="https://arxiv.org/abs/2608.15652", code="", tasks="source_attribution", scopes="fully_generated", types="method", affiliations=[aff("Tel Aviv University",["Asaf Livne","Amir Jevnisek","Shai Avidan"],"Tel Aviv University")], version="Current authoritative form is arXiv 2608.15652; no later publication was established. Attribution is passive image-to-generator inference."),
 dict(cid="audit:96a08f643278af6c", title="NeuroRenderedFake: A Challenging Benchmark to Detect Fake Images Generated by Advanced Neural Rendering Methods", year="2025", authors=["Chengdong Dong","Vijayakumar Bhagavatula","Zhenyu Zhou","Ajay Kumar"], venue="Advances in Neural Information Processing Systems", ptype="conference", doi="10.52202/085713-2012", arxiv="", oa="https://openalex.org/W7197051350", url="https://proceedings.neurips.cc/paper_files/paper/2025/hash/56bdf726a96d43ee1e66172d14c63a61-Abstract-Datasets_and_Benchmarks_Track.html", code="", tasks="detection", scopes="fully_generated", types="dataset;benchmark;analysis_study", affiliations=[aff("Carnegie Mellon University",["Chengdong Dong","Vijayakumar Bhagavatula"],"Department of Electrical and Computer Engineering, Carnegie Mellon University"),aff("The Hong Kong Polytechnic University",["Chengdong Dong","Zhenyu Zhou","Ajay Kumar"],"Department of Data Science and Artificial Intelligence, The Hong Kong Polytechnic University")], version="One NeurIPS 2025 Datasets and Benchmarks paper covering neural rendering and broader GAN/diffusion imagery."),
 dict(cid="audit:a1d31a96ac288ab0", title="ImageTrust: Multi-backbone Fusion for AI-Generated Image Detection with Calibrated Uncertainty", year="2027", authors=["Andrei-Alexandru Iancu","Darius Galiş","Sebastian-Aurelian Stefaniga"], venue="International Conference on Complex, Intelligent, and Software Intensive Systems", ptype="conference", doi="10.1007/978-3-032-29430-2_19", arxiv="", oa="https://openalex.org/W7208817080", url="https://doi.org/10.1007/978-3-032-29430-2_19", code="", tasks="detection", scopes="fully_generated", types="method", affiliations=[aff("West University of Timișoara",["Andrei-Alexandru Iancu","Darius Galiş","Sebastian-Aurelian Stefaniga"],"Faculty of Computer Science, West University of Timişoara, Timişoara, Romania")], version="Official Springer chapter is the canonical publication and gives publication year 2027; OpenAlex's 2026 year is not used."),
 dict(cid="audit:bb665e920e4e26be", title="UniShield: An Adaptive Multi-Agent Framework for Unified Forgery Image Detection and Localization", year="2025", authors=["Qing Huang","Zhipei Xu","Xuanyu Zhang","Xiangyu Yu","Jian Zhang"], venue="arXiv", ptype="preprint", doi="10.48550/arXiv.2510.03161", arxiv="2510.03161", oa="https://openalex.org/W4416371312", url="https://arxiv.org/abs/2510.03161", code="", tasks="detection;localization", scopes="fully_generated;generative_editing", types="method", affiliations=[aff("Peking University",["Qing Huang","Zhipei Xu","Xuanyu Zhang","Jian Zhang"],"School of Electronic and Computer Engineering; Guangdong Provincial Key Laboratory of Ultra High Definition Immersive Media Technology, Shenzhen Graduate School, Peking University"),aff("South China University of Technology",["Qing Huang","Xiangyu Yu"],"School of Future Technology; School of Electronic and Information Engineering, South China University of Technology")], version="Current authoritative form is arXiv 2510.03161. The relevant endpoint is passive detection/localization, not protection or watermarking."),
 dict(cid="audit:f49729ba31773bd0", title="Dual-scale model collaborative reasoning with multi-feature fusion for robust AI-generated image detection", year="2026", authors=["Jiaqi Han","Peiyan Zhong","Lingxin Sun"], venue="Multimedia Systems", ptype="journal", doi="10.1007/s00530-026-02425-4", arxiv="", oa="https://openalex.org/W7165519251", url="https://doi.org/10.1007/s00530-026-02425-4", code="", tasks="detection", scopes="fully_generated", types="method", affiliations=[aff("Qilu University of Technology",["Jiaqi Han"],"Qilu University of Technology (Shandong Academy of Sciences), Jinan, China"),aff("Chongqing University",["Peiyan Zhong"],"Chongqing University, Chongqing, China"),aff("Rochester Institute of Technology",["Lingxin Sun"],"College of Art and Design, Rochester Institute of Technology (RIT), Rochester, USA")], version="One final Multimedia Systems journal article; no separate preprint or proceedings version was established."),
]

ABSTRACTS = {
 "audit:07194f58b4540acc": "Generative AI has made text-guided inpainting a powerful image editing tool, but at the same time a growing challenge for media forensics. We introduce TGIF2, an extended version of TGIF, that captures recent advances in text-guided inpainting and enables a deeper analysis of forensic robustness. TGIF2 augments the original dataset with edits generated by FLUX.1 models, as well as with random non-semantic masks. Using the TGIF2 dataset, we conduct a forensic evaluation spanning image forgery localization and synthetic image detection, including fine-tuning localization methods on fully regenerated images and generative super-resolution attacks.",
 "audit:a1d31a96ac288ab0": "This paper proposes ImageTrust, a detection system which addresses poor performance after recompression and missing calibrated uncertainty estimates. ImageTrust concatenates embeddings from ResNet-50, EfficientNet-B0 and ViT-B/16, uses temperature scaling and conformal prediction, and is benchmarked on images generated by 24 generator architectures.",
 "audit:f49729ba31773bd0": "The rapid advancement of generative models has increasingly blurred the boundary between synthetic and real imagery. This paper presents a multi-module detection framework that integrates lightweight visual features, auxiliary descriptors, and a dual-scale model collaborative reasoning paradigm. Comparative and ablation experiments evaluate accuracy, stability, and generalization against VLM-based baselines.",
}

REVIEW_LOC = {"Ghent University":("Gent","Belgium"),"imec":("Gent","Belgium"),"BBC Research & Development":("",""),"Lenovo Research":("",""),"Reality Defender":("",""),"Wuhan University of Technology":("",""),"West University of Timișoara":("Timișoara","Romania"),"Chongqing University":("Chongqing","China"),"Rochester Institute of Technology":("Rochester","United States")}

def read(path):
    with path.open(newline="") as h: return list(csv.DictReader(h))

def write(path, columns, rows):
    with path.open("w", newline="") as h:
        w=csv.DictWriter(h, fieldnames=columns); w.writeheader(); w.writerows(rows)

def restore_baseline_and_append(path, columns, rows):
    """Preserve pre-task bytes and append reviewed rows with repository LF endings."""
    baseline = OUT / "baseline" / path.relative_to(ROOT)
    original = baseline.read_bytes()
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writerows(rows)
    separator = b"" if not original or original.endswith(b"\n") else b"\n"
    path.write_bytes(original + separator + buffer.getvalue().encode("utf-8"))

def snapshot():
    base=OUT/"baseline"; hashes={}
    for rel in ["data/curated/papers.csv","data/curated/paper_taxonomy.csv","data/curated/author_institution_mappings.csv","data/curated/institutions.csv","data/curated/institution_location_review.csv","data/curated/institution_locations.csv","data/curated/institution_aliases.csv","data/curated/institution_hierarchy.csv","data/curated/paper_exclusions.csv","web/data/public_preview_papers.json","web/data/public_preview_map_data.json"]:
        p=ROOT/rel; hashes[rel]=hashlib.sha256(p.read_bytes()).hexdigest(); t=base/rel; t.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,t)
    (OUT/"baseline_sha256.json").write_text(json.dumps(hashes,indent=2,sort_keys=True)+"\n")

def build():
    queue={r["candidate_id"]:r for r in read(QUEUE)}
    assert set(queue)=={p["cid"] for p in PAPERS} and len(PAPERS)==12
    existing_insts={r["institution_id"]:r for r in read(ROOT/"data/curated/institutions.csv")}
    inst_name={r["institution_id"]:r["canonical_name"] for r in existing_insts.values()}
    inst_name.update({r["institution_id"]:r["canonical_name"] for r in NEW.values()})
    locs={r["institution_id"]:r for r in read(ROOT/"data/curated/institution_locations.csv") if r["coordinate_status"]=="confirmed"}
    paper_rows=[]; tax_rows=[]; mapping_rows=[]; review_rows=[]; proposals=[]
    for p in PAPERS:
        pid=paper_id(p["cid"]); q=queue[p["cid"]]; abstract=ABSTRACTS.get(p["cid"],q["saved_evidence"]); title=canonical_paper_title(p["title"])
        row=dict.fromkeys(PAPERS_COLUMNS,""); row.update(paper_id=pid,title=title,year=p["year"],authors=", ".join(p["authors"]),venue=p["venue"],raw_venue=p["venue"],doi=p["doi"],arxiv_id=p["arxiv"],openalex_url=p["oa"],paper_url=p["url"],publication_type=p["ptype"],abstract=abstract,tasks=p["tasks"],image_scopes=p["scopes"],research_types=p["types"],scope_status="in_scope",source_database="primary_source",metadata_source=p["url"],curation_status="confirmed",review_status="reviewed",created_at=NOW,updated_at=NOW)
        row=canonicalize_record(row); paper_rows.append({k:row.get(k,"") for k in PAPERS_COLUMNS})
        tr=dict.fromkeys(PAPER_TAXONOMY_COLUMNS,""); tr.update(taxonomy_id="paper_id:"+pid,paper_id=pid,title=title,year=p["year"],doi=p["doi"],arxiv_id=p["arxiv"],openalex_url=p["oa"],tasks=p["tasks"],image_scopes=p["scopes"],research_types=p["types"],taxonomy_status="reviewed",audited_at="2026-09-19")
        for dim in ("tasks","image_scopes","research_types"):
            evidence=abstract[:700]
            if dim=="tasks" and "localization" in p["tasks"]:
                evidence += " The primary paper explicitly evaluates forgery localization as well as detection."
            if dim=="image_scopes" and "generative_editing" in p["scopes"]:
                evidence += " The evaluated inputs contain generative edits, diffusion manipulations, or text-guided inpainting."
            tr[dim+"_status"]="reviewed"; tr[dim+"_review_reason"]="Primary-source review under the narrowed Tier 2 inclusion policy."; tr[dim+"_evidence_tier"]="primary_paper"; tr[dim+"_evidence_source"]=p["url"]; tr[dim+"_evidence_excerpt"]=evidence
        tax_rows.append(tr)
        verified=[]
        for n,a in enumerate(p["affiliations"],1):
            iid=EXISTING.get(a["institution"],NEW.get(a["institution"],{}).get("institution_id")); assert iid, a
            loc=locs.get(iid,{})
            mr=dict.fromkeys(AUTHOR_INSTITUTION_MAPPING_COLUMNS,""); mr.update(mapping_id=hid("mapping:",pid+":"+str(n),20),paper_id=pid,title=title,year=p["year"],doi=p["doi"],openalex_url=p["oa"],institution=inst_name[iid],institution_id=iid,location_id=loc.get("location_id",""),institution_authors="; ".join(a["authors"]),author_order="; ".join(str(p["authors"].index(x)+1) for x in a["authors"]),affiliation_order=str(n),raw_affiliation=a["raw"],institution_city=loc.get("city",""),institution_country=loc.get("country",""),institution_latitude=loc.get("lat",""),institution_longitude=loc.get("lon",""),provenance_source=p["url"],mapping_status="active",created_at=NOW,updated_at=NOW)
            mapping_rows.append(mr); verified.append({"institution":inst_name[iid],"institution_id":iid,"authors":a["authors"],"raw_affiliation":a["raw"]})
        proposals.append({**p,"title":title,"paper_id":pid,"policy_rationale":q["qualifying_synthetic_image_contribution"],"abstract":abstract,"verified_affiliations":verified})
    for name,inst in NEW.items():
        p=next(p for p in PAPERS if any(a["institution"]==name for a in p["affiliations"])); a=next(a for a in p["affiliations"] if a["institution"]==name); city,country=REVIEW_LOC[name]
        rr=dict.fromkeys(INSTITUTION_LOCATION_REVIEW_COLUMNS,""); rr.update(institution=name,canonical_institution_name=name,institution_id=inst["institution_id"],related_paper_id=paper_id(p["cid"]),title=p["title"],year=p["year"],doi=p["doi"],openalex_url=p["oa"],institution_authors="; ".join(a["authors"]),raw_affiliation=a["raw"],evidence_source="Primary paper author-affiliation block",evidence_url=p["url"],suggested_city=city,suggested_country=country,suggested_canonical_institution=name,match_method="primary_affiliation_exact",confidence="high" if city and country else "medium",review_status="pending_review",location_status="needs_coordinate_review",coordinate_status="missing",created_at=NOW,updated_at=NOW)
        review_rows.append(rr)
    return {"papers.csv":paper_rows,"paper_taxonomy.csv":tax_rows,"author_institution_mappings.csv":mapping_rows,"institutions.csv":list(NEW.values()),"institution_location_review.csv":review_rows,"proposals":proposals}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    receipt=OUT/"insertion.json"; additions=build()
    (OUT/"planned_additions.json").write_text(json.dumps(additions,indent=2,ensure_ascii=False)+"\n")
    if receipt.exists():
        targets={"papers.csv":PAPERS_COLUMNS,"paper_taxonomy.csv":PAPER_TAXONOMY_COLUMNS,"author_institution_mappings.csv":AUTHOR_INSTITUTION_MAPPING_COLUMNS,"institutions.csv":INSTITUTION_COLUMNS,"institution_location_review.csv":INSTITUTION_LOCATION_REVIEW_COLUMNS}
        for name,cols in targets.items():
            path=ROOT/"data/curated"/name
            restore_baseline_and_append(path,cols,additions[name])
        print(receipt.read_text(),end=""); return
    snapshot()
    targets={"papers.csv":PAPERS_COLUMNS,"paper_taxonomy.csv":PAPER_TAXONOMY_COLUMNS,"author_institution_mappings.csv":AUTHOR_INSTITUTION_MAPPING_COLUMNS,"institutions.csv":INSTITUTION_COLUMNS,"institution_location_review.csv":INSTITUTION_LOCATION_REVIEW_COLUMNS}
    for name,cols in targets.items():
        path=ROOT/"data/curated"/name; old=read(path); new=additions[name]
        keys={r[next(iter(cols))] for r in old}; assert not any(r[next(iter(cols))] in keys for r in new)
        write(path,cols,old+new)
    result={"papers_added":12,"taxonomy_rows_added":12,"mappings_added":len(additions["author_institution_mappings.csv"]),"institutions_added":len(NEW),"location_reviews_added":len(additions["institution_location_review.csv"]),"created_at":NOW}
    receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n"); print(json.dumps(result,indent=2))

if __name__ == "__main__": main()
