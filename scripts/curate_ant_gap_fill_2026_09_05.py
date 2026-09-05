#!/usr/bin/env python3
"""Apply the closed 2026-09-05 Ant/AI-edit literature gap-fill decisions."""

from __future__ import annotations

import csv
import hashlib
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from curated_mappings import create_mapping_candidates
from curated_institutions import (
    load_institutions,
    merge_institutions,
    update_institution_location,
)
from curated_papers import (
    create_curated_paper,
    existing_canonical_match,
    read_curated_papers,
    write_curated_papers,
)
from curated_schema import PAPER_EXCLUSION_COLUMNS, PAPER_TAXONOMY_COLUMNS


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/ant_gap_fill_2026_09_05"
PAPERS = ROOT / "data/curated/papers.csv"
MAPPINGS = ROOT / "data/curated/author_institution_mappings.csv"
EXCLUSIONS = ROOT / "data/curated/paper_exclusions.csv"
TAXONOMY = ROOT / "data/curated/paper_taxonomy.csv"
PUBLIC_PAPERS = ROOT / "web/data/public_preview_papers.json"
PUBLIC_MAP = ROOT / "web/data/public_preview_map_data.json"
INSTITUTION_AUDIT = ROOT / "data/curated/institution_audit_log.csv"
AUDITED_AT = "2026-09-05"
CREATED_BY = "codex_ant_gap_fill_20260905"


ADD_IDS = (
    "2406.16531", "2410.02761", "2505.18660", "2506.00979",
    "2507.14632", "2509.14957", "2509.25502", "2511.08423",
    "2511.12363", "2511.12511", "2511.19111", "2512.06746",
    "2602.01738", "2602.02222", "2602.10042", "2602.21716",
    "2603.23115", "2604.02694", "2604.08211", "2604.28177",
    "2605.08820", "2605.14091", "2605.14486", "2605.21977",
    "2605.26421", "2606.08634", "2606.31082", "2607.14684",
    "2607.27113", "2608.09223", "2608.12811", "2608.12876",
    "2608.16259", "2608.16646", "2608.18968", "2608.20929",
    "2608.28302",
)


LABELS = {
    "2406.16531": ("detection;localization", "generative_editing", "method;dataset;benchmark"),
    "2410.02761": ("detection;localization", "generative_editing;deepfake;traditional_manipulation", "method;dataset"),
    "2505.18660": ("detection;localization", "fully_generated", "method;dataset;benchmark"),
    "2506.00979": ("detection", "fully_generated;deepfake", "method;dataset;benchmark"),
    "2507.14632": ("detection", "fully_generated", "method;dataset;benchmark"),
    "2509.14957": ("detection", "fully_generated", "method"),
    "2509.25502": ("detection", "fully_generated", "method;benchmark"),
    "2511.08423": ("detection", "fully_generated", "method;dataset;benchmark"),
    "2511.12363": ("detection", "fully_generated", "dataset;benchmark;analysis_study"),
    "2511.12511": ("detection", "fully_generated", "method"),
    "2511.19111": ("detection;source_attribution;localization", "generative_editing", "dataset;benchmark;analysis_study"),
    "2512.06746": ("detection", "fully_generated", "method;analysis_study"),
    "2602.01738": ("detection", "fully_generated", "method;analysis_study"),
    "2602.02222": ("detection", "fully_generated", "method;dataset;benchmark"),
    "2602.10042": ("detection", "fully_generated", "method;dataset"),
    "2602.21716": ("detection", "fully_generated", "method"),
    "2603.23115": ("detection", "fully_generated", "method"),
    "2604.02694": ("detection;localization", "generative_editing;traditional_manipulation", "method;dataset;benchmark"),
    "2604.08211": ("detection", "fully_generated", "dataset;benchmark;analysis_study"),
    "2604.28177": ("detection;localization", "fully_generated;generative_editing", "benchmark;analysis_study"),
    "2605.08820": ("detection", "fully_generated;generative_editing", "dataset;benchmark;analysis_study"),
    "2605.14091": ("detection;localization", "fully_generated;generative_editing;deepfake;traditional_manipulation", "method;benchmark;analysis_study"),
    "2605.14486": ("detection", "fully_generated", "method;analysis_study"),
    "2605.21977": ("detection", "fully_generated", "method;analysis_study"),
    "2605.26421": ("detection", "fully_generated", "method"),
    "2606.08634": ("detection", "fully_generated", "method;analysis_study"),
    "2606.31082": ("detection", "fully_generated", "method;dataset;benchmark"),
    "2607.14684": ("detection", "fully_generated", "method;analysis_study"),
    "2607.27113": ("detection", "fully_generated", "method"),
    "2608.09223": ("detection", "fully_generated", "method;analysis_study"),
    "2608.12811": ("detection", "fully_generated", "method"),
    "2608.12876": ("detection", "fully_generated;generative_editing", "method"),
    "2608.16259": ("detection;localization", "fully_generated", "method;dataset"),
    "2608.16646": ("detection", "fully_generated", "analysis_study"),
    "2608.18968": ("localization", "generative_editing;traditional_manipulation", "method;analysis_study"),
    "2608.20929": ("localization", "generative_editing", "method;dataset;analysis_study"),
    "2608.28302": ("detection;localization", "generative_editing", "method"),
}


TITLE_OVERRIDES = {
    "2505.18660": "So-Fake: Benchmarking Social-Media Image Forgery Detection",
    "2603.23115": "AgentFoX: LLM-Driven Agentic Multi-Expert Fusion with Explainability for AI-Generated Image Detection",
    "2605.14486": "Reduce the Artifact Bias for More Generalizable AI-Generated Image Detection",
}


TAXONOMY_EVIDENCE_SUFFIX = {
    "2604.02694": (
        "PDF evidence: the paper identifies copy-move or generative inpainting "
        "as probable document-forgery mechanisms."
    ),
    "2604.28177": (
        "PDF figure evidence: Manipulation Classification, Tampering Pinpointing, "
        "and Targeted Region Editing are evaluated forensic perspectives."
    ),
}


FORMAL = {
    "2406.16531": {
        "year": "2025", "venue": "Proceedings of the AAAI Conference on Artificial Intelligence",
        "venue_id": "venue:aaai", "venue_name": "Proceedings of the AAAI Conference on Artificial Intelligence",
        "venue_acronym": "AAAI", "venue_type": "conference", "venue_track": "main",
        "raw_venue": "AAAI-25 Technical Track on Computer Vision I",
        "doi": "10.1609/aaai.v39i2.32231", "openalex_url": "https://openalex.org/W4409346508",
        "paper_url": "https://ojs.aaai.org/index.php/AAAI/article/view/32231",
        "publication_type": "conference",
    },
    "2410.02761": {
        "year": "2025", "venue": "International Conference on Learning Representations",
        "venue_id": "venue:iclr", "venue_name": "International Conference on Learning Representations",
        "venue_acronym": "ICLR", "venue_type": "conference", "venue_track": "main",
        "raw_venue": "International Conference on Learning Representations 2025",
        "doi": "10.48550/arxiv.2410.02761", "openalex_url": "https://openalex.org/W4403884296",
        "paper_url": "https://proceedings.iclr.cc/paper_files/paper/2025/hash/4d4e0ab9d8ff180bf5b95c258842d16e-Abstract-Conference.html",
        "publication_type": "conference",
    },
}


OPENALEX = {
    "2509.14957": "W4417077675", "2511.12363": "W4416355068",
    "2511.12511": "W4416355395", "2602.01738": "W7127417793",
    "2602.02222": "W7127306890", "2602.10042": "W7128616555",
    "2602.21716": "W7131638568", "2603.23115": "W7140286693",
    "2604.02694": "W7150836396", "2604.08211": "W7153340200",
    "2604.28177": "W7159651702", "2605.08820": "W7160919986",
    "2605.14091": "W7161247325", "2605.26421": "W7162539349",
    "2606.08634": "W7164005994", "2607.14684": "W7169576517",
    "2607.27113": "W7171865953", "2608.09223": "W7202162876",
    "2608.12876": "W7203457219", "2608.16259": "W7203680892",
    "2608.16646": "W7203677886", "2608.17700": "W7203745753",
    "2608.18573": "W7203862485", "2608.18968": "W7203861168",
    "2608.20713": "W7204111771", "2608.20929": "W7204102515",
    "2608.28302": "W7204850927", "2511.19111": "W7106655390",
    "2512.06746": "W7110829309", "2512.23374": "W7117726997",
    "2505.12620": "W4417301672", "2506.00979": "W4414894364",
    "2507.14632": "W4417429931", "2508.21048": "W4414452097",
    "2511.08423": "W4416184934", "2406.13495": "W4399912913",
    "2410.21964": "W4404341445", "2411.19715": "W4405031434",
    "2501.04376": "W4406231339", "2410.02761": "W4403884296",
}


def m(institution: str, authors: str, raw: str | None = None) -> dict[str, object]:
    return {
        "institution": institution,
        "institution_authors": [name.strip() for name in authors.split(";") if name.strip()],
        "raw_affiliation": raw or institution,
        "provenance_source": "authoritative arXiv PDF first-page/author-affiliation section",
        "mapping_status": "active",
    }


MAPPING_DRAFTS = {
    "2406.16531": [
        m("Shanghai Jiao Tong University", "Yirui Chen; Jie Yang; Wei Liu"),
        m("Tsinghua University", "Quan Zhang"),
        m("Huawei Noah's Ark Lab", "Yirui Chen; Xudong Huang; Quan Zhang; Wei Li; Mingjian Zhu; Qiangyu Yan; Simiao Li; Hanting Chen; Hailin Hu; Jie Hu"),
    ],
    "2410.02761": [
        m("Peking University", "Zhipei Xu; Xuanyu Zhang; Runyi Li; Zecheng Tang; Jian Zhang", "School of Electronic and Computer Engineering / Shenzhen Graduate School, Peking University"),
        m("South China University of Technology", "Qing Huang", "School of Future Technology, South China University of Technology"),
    ],
    "2505.18660": [
        m("University of Liverpool", "Zhenglin Huang; Xiaowei Huang; Guangliang Cheng"),
        m("The Hong Kong University of Science and Technology", "Xi Yang"),
        m("University of Sheffield", "Bei Peng"),
        m("The Chinese University of Hong Kong, Shenzhen", "Baoyuan Wu"),
        m("Nanyang Technological University", "Xiangtai Li; Dacheng Tao"),
        m("University of California, Merced", "Ming-Hsuan Yang"),
    ],
    "2506.00979": [
        m("Nanjing University", "Wenhui Dong; Chenyang Si; Caifeng Shan"),
        m("Wuhan University", "Changjiang Jiang; Fengchang Yu"), m("Stanford University", "Wei Peng"),
        m("Ningxia University", "Zhonghao Zhang"), m("Nankai University", "Xinbin Yuan"),
        m("Georgia Institute of Technology", "Yifei Bi"), m("Jilin University", "Ming Zhao"),
        m("Zhejiang University", "Zian Zhou"),
    ],
    "2507.14632": [m("University of Liverpool", "Haiquan Wen; Tianxiao Li; Zhenglin Huang; Yiwei He; Guangliang Cheng")],
    "2509.14957": [
        m("East China Normal University", "Zhuokang Shen; Kaisen Zhang; Bohan Jia; Yuan Fang; Zhou Yu; Shaohui Lin"),
        m("Sanming University", "Heming Jia; Shaohui Lin"),
        m("The 27th Research Institute of China Electronics Technology Group Corporation", "Zhou Yu"),
    ],
    "2509.25502": [
        m("Shenzhen University", "Kaiqing Lin; Yue Zhou; Bin Li"),
        m("Tencent Youtu Lab", "Kaiqing Lin; Zhiyuan Yan; Ruoxin Chen; Ke-Yue Zhang; Taiping Yao; Shouhong Ding"),
        m("Peking University", "Zhiyuan Yan; Peng Jin"), m("Sun Yat-sen University", "Junyan Ye"),
    ],
    "2511.08423": [
        m("Shanghai Artificial Intelligence Laboratory", "Yuncheng Guo; Junyan Ye; Hengrui Kang; Conghui He; Weijia Li"),
        m("Sun Yat-sen University", "Junyan Ye"),
        m("Tsinghua Shenzhen International Graduate School", "Chenjue Zhang; Haohuan Fu; Weijia Li"),
        m("Shanghai Jiao Tong University", "Hengrui Kang"),
    ],
    "2511.12363": [
        m("The University of Texas at Dallas", "Michael Yang; Shijian Deng; William T. Doan; Yapeng Tian"),
        m("University of Toronto", "Kai Wang"), m("University of Notre Dame", "Tianyu Yang"),
        m("Stony Brook University", "Harsh Singh"),
    ],
    "2511.12511": [
        m("The University of Sydney", "Jialiang Shen; Jiyang Zheng; Yu Yao; Hui Kang; Tongliang Liu"),
        m("CSIRO", "Jiyang Zheng; Dadong Wang", "CSIRO Data61"),
        m("Shanghai Jiao Tong University", "Yunqi Xue; Helin Gong; Yang Yang"),
        m("City University of Macau", "Huajie Chen"),
        m("Institute of Automation, Chinese Academy of Sciences", "Ruiqi Liu", "CASIA"),
    ],
    "2511.19111": [m("National University of Singapore", "Hai Ci; Pei Yang; Yingxin Xuan; Mike Zheng Shou", "Show Lab, National University of Singapore"), m("South China University of Technology", "Ziheng Peng")],
    "2512.06746": [
        m("Tencent Youtu Lab", "Ruoxin Chen; Keyue Zhang; Yandan Zhao; Taiping Yao; Shouhong Ding"),
        m("East China University of Science and Technology", "Jiahui Gao"),
        m("Shenzhen University", "Kaiqing Lin"), m("The Hong Kong University of Science and Technology", "Isabel Guan"),
    ],
    "2602.01738": [m("Shenzhen University", "Yue Zhou; Kaiqing Lin; Bin Li"), m("Nanchang University", "Xinan He; Feng Ding"), m("University of North Texas", "Bing Fan")],
    "2602.02222": [
        m("Institute of Automation, Chinese Academy of Sciences", "Ruiqi Liu; Ziheng Qin; Zhiheng Li; Junkai Chen; ZhiJin Chen; Lubin Weng; Jing Dong; Shu Wu"),
        m("University of Chinese Academy of Sciences", "Ruiqi Liu"), m("Huazhong University of Science and Technology", "Manni Cui"),
        m("Tencent Youtu Lab", "Ruoxin Chen"), m("Southwest University", "Yi Han"), m("Peking University", "Zhiyuan Yan"),
        m("The University of Sydney", "Jialiang Shen"), m("Shenzhen University", "Kaiqing Lin"), m("Tsinghua University", "Yan Wang"),
    ],
    "2602.10042": [m("Wuhan University", "Changjiang Jiang; Fengchang Yu; Wei Lu"), m("Ant Group", "Changjiang Jiang; Xinkuan Sha; Jingjing Liu; Jian Liu; Mingqi Fang; Chenfeng Zhang"), m("Zhejiang University", "Chenfeng Zhang")],
    "2602.21716": [m("Wuhan University", "Wenbin Wang; Yong Luo"), m("Tencent Youtu Lab", "Yuge Huang; Jianqing Xu; Yue Yu; Jiangtao Yan; Shouhong Ding"), m("Singapore Management University", "Pan Zhou")],
    "2603.23115": [
        m("Shenzhen University", "Yangxin Yu; Bin Li; Yue Zhou; Kaiqing Lin; Haodong Li"),
        m("Sun Yat-sen University", "Jiangqun Ni", "School of Cyber Science and Technology, Sun Yat-sen University"),
        m("China Electronics Technology Group Corporation", "Bo Cao", "Smart City Research Institute of China Electronics Technology Group Corporation"),
    ],
    "2604.02694": [m("Ant Group", "Fanwei Zeng; Changtao Miao; Jing Huang; Zhiya Tan; Shutao Gong; Xiaoming Yu; Yang Wang; Weibin Yao; Jianshu Li; Ying Yan"), m("Nanyang Technological University", "Zhiya Tan"), m("Agency for Science, Technology and Research", "Joey Tianyi Zhou", "CFAR and IHPC, Agency for Science, Technology and Research (A*STAR), Singapore")],
    "2604.08211": [m("Zhejiang University", "You Hu; Changfa Mo; Xiaobai Li"), m("University of Oulu", "Haotian Liu")],
    "2604.28177": [m("Beijing University of Posts and Telecommunications", "Bo Zhang; Tzu-Yen Ma; Zichen Tang; Junpeng Ding; Zirui Wang; Yizhuo Zhao; Peilin Gao; Zijie Xi; Zixin Ding; Haiyang Sun; Haocheng Gao; Yuan Liu; Liangjia Wang; Yiling Huang; Yujie Wang; Yuyue Zhang; Ronghui Xi; Yuanze Li; Jiacheng Liu; Zhongjun Yang; Haihong E")],
    "2605.08820": [m("Nanyang Technological University", "Xinyu Yan; Boyang Chen; Jiaming Zhang; Tiantong Wu; Hong Xi Tae; Yichen He; Tiantong Wang; Yachun Mi; Yurong Hao; Yilei Zhao; Wei Yang Bryan Lim"), m("Alibaba Group", "Lei Xiao; Longtao Huang; Pengjun Xie; Wei Liu")],
    "2605.14091": [m("Ant Group", "GuangJian Team")],
    "2605.14486": [
        m("University of Chinese Academy of Sciences", "Yiheng Li; Yang Yang; Zhen Lei"),
        m("Institute of Automation, Chinese Academy of Sciences", "Yiheng Li; Yang Yang; Zhen Lei"),
        m("University of Technology Sydney", "Wenhao Wang"), m("Sangfor Technologies", "Zichang Tan"),
        m("Tsinghua University", "Zecheng Lin"), m("China Mobile Financial Technology Co., Ltd.", "Li Gao"),
        m("Hong Kong Institute of Science and Innovation, Chinese Academy of Sciences", "Zhen Lei"),
        m("Macau University of Science and Technology", "Zhen Lei"),
    ],
    "2605.21977": [m("Harbin Institute of Technology, Shenzhen", "Zhengcen Li; Chenyang Jiang; Liangxu Su; Tong Shao; Shiyang Zhou; Jingyong Su"), m("Pengcheng Laboratory", "Ming Tao"), m("Shenzhen Loop Area Institute", "Shiyang Zhou")],
    "2605.26421": [m("Beijing University of Posts and Telecommunications", "Senyuan Shi; Shuhan Feng"), m("University of Chinese Academy of Sciences", "Hao Tan"), m("Shenzhen Institute of Advanced Technology, Chinese Academy of Sciences", "Zichang Tan"), m("Institute of Automation, Chinese Academy of Sciences", "Hao Tan; Ajian Liu; Jun Wan"), m("University of Barcelona", "Sergio Escalera")],
    "2606.08634": [m("Korea Advanced Institute of Science and Technology", "Seunghyun Lee; Byoungkwon Kim; Kyungmin Lee; Jinwoo Shin", "KAIST"), m("Google Cloud AI", "Jaehyun Nam")],
    "2606.31082": [m("Institute of Computing Technology, Chinese Academy of Sciences", "Jiaan Wang; Sirui Liu; Yu Li; Kaiyuan Yang; Juan Cao; Sheng Tang"), m("University of Chinese Academy of Sciences", "Jiaan Wang; Kaiyuan Yang"), m("Hangzhou Institute for Advanced Study, University of Chinese Academy of Sciences", "Sirui Liu")],
    "2607.14684": [m("Huazhong University of Science and Technology", "Manni Cui; Dianyuan Zou; Jingrui Xu; Jianglan Wei; Han Zhou; Yu Liu"), m("Institute of Automation, Chinese Academy of Sciences", "Ruiqi Liu; Ziheng Qin; Shu Wu"), m("Jilin University", "ZiAn Wang"), m("Tsinghua University", "Yan Wang")],
    "2607.27113": [m("University of Chinese Academy of Sciences", "Hao Tan; Jun Wan; Zhen Lei"), m("Institute of Automation, Chinese Academy of Sciences", "Hao Tan; Ajian Liu; Jun Wan; Zhen Lei"), m("Ant Group", "Jun Lan; Zijian Yu; Chuanbiao Song; Huijia Zhu; Weiqiang Wang"), m("Sangfor Technologies", "Zichang Tan")],
    "2608.09223": [m("Beijing Institute of Technology, Zhuhai", "Shengbo Qi; Hongyi Fang; Benjia Zhou"), m("Shenzhen University", "Rui Mao")],
    "2608.12811": [m("Zhejiang University", "Jiazhen Yang; Zunlei Feng"), m("Taobao & Tmall Group", "Ruijin Jin; Junjun Zheng; Xiangheng Kong"), m("Zhejiang University of Technology", "Jie Lei")],
    "2608.12876": [m("East China Normal University", "Yicheng Bao; Xiahui Guo; Xin Tan"), m("Shanghai Artificial Intelligence Laboratory", "Xuhong Wang; Xin Tan")],
    "2608.16259": [m("Shanghai Jiao Tong University", "Bowen Deng; Jiahui Zhan; Yikun Ji; Haozhen Yan; Jianfu Zhang")],
    "2608.16646": [m("Ruhr University Bochum", "Roman Demchenko; Jonas Ricker; Asja Fischer")],
    "2608.18968": [m("St Paul's School, London", "Zane Kumar"), m("Imperial College London", "Vishal Jain; Bernhard Kainz"), m("Friedrich-Alexander-Universitaet Erlangen-Nuernberg", "Bernhard Kainz", "FAU Erlangen-Nuernberg")],
    "2608.20929": [m("Shanghai Jiao Tong University", "Haozhen Yan; Siyuan Shan; Jianfu Zhang"), m("Ant Group", "Zijian Yu; Yan Hong; Jun Lan"), m("Shenzhen University", "Youqi Wang")],
    "2608.28302": [m("University of Amsterdam", "Anton Nuzhdin; Marcel Worring; Ivona Najdenkoska", "Informatics Institute, University of Amsterdam")],
}


EXCLUDED = {
    "2608.20713": ("out_of_scope", "Generation-quality/defect diagnosis; authenticity is not the target."),
    "2606.17433": ("out_of_scope", "Logical-anomaly reasoning benchmark, not image authenticity forensics."),
    "2604.25370": ("out_of_scope", "Collection and characterization of self-reported generated images without a forensic task or benchmark."),
    "2508.21048": ("deepfake_only_not_core", "Deepfake-only face-forensics paper."),
    "2505.12620": ("out_of_scope", "Video-only AIGC detection and explanation."),
    "2506.23292": ("deepfake_only_not_core", "Deepfake-only image/video dataset."),
    "2406.13495": ("deepfake_only_not_core", "Deepfake-only benchmark and detector study."),
    "2608.20913": ("deepfake_only_not_core", "Deepfake-only explainable detector."),
    "2608.18573": ("deepfake_only_not_core", "Deepfake-only forensic framework."),
    "2603.21526": ("deepfake_only_not_core", "Deepfake-only reasoning detector."),
    "2608.17700": ("deepfake_only_not_core", "Deepfake-only detector."),
    "2411.19715": ("deepfake_only_not_core", "Face-forgery-only detector."),
    "2501.04376": ("deepfake_only_not_core", "Deepfake-only detector."),
    "2410.21964": ("deepfake_only_not_core", "Deepfake-only detector."),
}


def read_arxiv_entries() -> dict[str, dict[str, object]]:
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    entries: dict[str, dict[str, object]] = {}
    for path in (RAW / "ant_candidates_arxiv.xml", RAW / "gim_arxiv.xml"):
        root = ET.parse(path).getroot()
        for entry in root.findall("atom:entry", namespace):
            arxiv_id = entry.findtext("atom:id", "", namespace).rsplit("/", 1)[-1].split("v", 1)[0]
            entries[arxiv_id] = {
                "title": " ".join(entry.findtext("atom:title", "", namespace).split()),
                "authors": [" ".join(author.findtext("atom:name", "", namespace).split()) for author in entry.findall("atom:author", namespace)],
                "abstract": " ".join(entry.findtext("atom:summary", "", namespace).split()),
                "published": entry.findtext("atom:published", "", namespace)[:10],
            }
    return entries


def paper_draft(arxiv_id: str, entry: dict[str, object]) -> dict[str, object]:
    tasks, scopes, types = LABELS[arxiv_id]
    year = str(entry["published"])[:4]
    draft: dict[str, object] = {
        "title": TITLE_OVERRIDES.get(arxiv_id, entry["title"]), "year": year,
        "authors": entry["authors"], "venue": "arXiv", "venue_id": "venue:arxiv",
        "venue_name": "arXiv", "venue_acronym": "", "venue_type": "preprint",
        "venue_track": "", "raw_venue": "arXiv.org",
        "doi": f"10.48550/arxiv.{arxiv_id}", "arxiv_id": arxiv_id,
        "openalex_url": f"https://openalex.org/{OPENALEX[arxiv_id]}" if arxiv_id in OPENALEX else "",
        "paper_url": f"https://arxiv.org/abs/{arxiv_id}", "publication_type": "preprint",
        "abstract": entry["abstract"], "tasks": tasks.split(";"),
        "image_scopes": scopes.split(";"), "research_types": types.split(";"),
        "scope_status": "in_scope", "source_database": "manual",
        "metadata_source": "arXiv/publisher", "curation_status": "confirmed",
        "review_status": "reviewed",
    }
    draft.update(FORMAL.get(arxiv_id, {}))
    return draft


def append_taxonomy(curated: dict[str, str], arxiv_id: str, abstract: str) -> bool:
    with TAXONOMY.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    tasks, scopes, types = LABELS[arxiv_id]
    source = FORMAL.get(arxiv_id, {}).get("paper_url") or f"https://arxiv.org/abs/{arxiv_id}"
    excerpt = " ".join((abstract, TAXONOMY_EVIDENCE_SUFFIX.get(arxiv_id, ""))).strip()
    existing = next((row for row in rows if row["paper_id"] == curated["paper_id"]), None)
    row = existing if existing is not None else dict.fromkeys(PAPER_TAXONOMY_COLUMNS, "")
    desired = {
        "taxonomy_id": f"paper_id:{curated['paper_id']}", "paper_id": curated["paper_id"],
        "title": curated["title"], "year": curated["year"], "doi": curated["doi"],
        "arxiv_id": arxiv_id, "openalex_url": curated["openalex_url"],
        "tasks": tasks, "image_scopes": scopes, "research_types": types,
        "tasks_status": "reviewed", "tasks_evidence_tier": "authoritative_abstract",
        "tasks_evidence_source": source, "tasks_evidence_excerpt": excerpt,
        "image_scopes_status": "reviewed", "image_scopes_evidence_tier": "authoritative_abstract+pdf",
        "image_scopes_evidence_source": source, "image_scopes_evidence_excerpt": excerpt,
        "research_types_status": "reviewed", "research_types_evidence_tier": "authoritative_abstract",
        "research_types_evidence_source": source, "research_types_evidence_excerpt": excerpt,
        "taxonomy_status": "reviewed", "audited_at": AUDITED_AT,
    }
    changed = any(row.get(key) != value for key, value in desired.items())
    row.update(desired)
    if existing is None:
        rows.append(row)
    if not changed:
        return False
    temporary = TAXONOMY.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAPER_TAXONOMY_COLUMNS, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    temporary.replace(TAXONOMY)
    return existing is None


def reconcile_csiro_identity() -> bool:
    """Merge the source acronym into the pre-existing canonical CSIRO entity."""
    source_id = "institution:28c87720a5359633"
    target_id = "institution:3da00d58d4c97192"
    institutions = {row["institution_id"]: row for row in load_institutions()}
    source = institutions.get(source_id)
    if source is None or source.get("institution_status") != "active":
        return False
    merge_institutions(
        source_id, target_id,
        confirmation="REPLACE CSIRO WITH Commonwealth Scientific and Industrial Research Organisation GLOBALLY",
        review_note=(
            "2026-09-05 Ant gap-fill reconciliation: the DINO-Detect PDF uses "
            "CSIRO Data61, which is the existing Commonwealth Scientific and "
            "Industrial Research Organisation canonical entity."
        ),
    )
    return True


def synchronize_csiro_location_review() -> None:
    """Reuse the already confirmed CSIRO location for the new acronym mapping."""
    update_institution_location(
        "institution:3da00d58d4c97192",
        {
            "institution_id": "institution:3da00d58d4c97192",
            "loaded_institution_id": "institution:3da00d58d4c97192",
            "location_id": "location:11b19a7d5a729b52836b",
            "city": "Perth", "region": "Western Australia",
            "country": "Australia", "country_code": "AU",
            "lat": "-31.9495086", "lon": "115.7896174",
            "coordinate_status": "known", "created_by": CREATED_BY,
        },
        location_reviews_path=ROOT / "data/curated/institution_location_review.csv",
    )


def ensure_kaist_location() -> bool:
    """Promote the repository's cached ROR resolution for the SSAFE mapping."""
    locations_path = ROOT / "data/curated/institution_locations.csv"
    with locations_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    institution_id = "institution:148a0feafd311a0a"
    existing = next((row for row in rows if row["institution_id"] == institution_id), None)
    draft = {
        "institution_id": institution_id, "loaded_institution_id": institution_id,
        "city": "Daejeon", "region": "", "country": "South Korea",
        "country_code": "KR", "lat": "36.34913", "lon": "127.38493",
        "coordinate_status": "known", "created_by": CREATED_BY,
    }
    if existing is None:
        draft["create_new_location"] = True
    else:
        draft["location_id"] = existing["location_id"]
    update_institution_location(institution_id, draft)
    return existing is None


def append_exclusion(title: str, year: str, doi: str, openalex_url: str, reason: str, note: str) -> bool:
    with EXCLUSIONS.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if any(row["doi"].casefold() == doi.casefold() for row in rows if row["doi"]):
        return False
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    seed = f"{title}|{doi}|{reason}"
    row = dict.fromkeys(PAPER_EXCLUSION_COLUMNS, "")
    row.update({
        "exclusion_id": f"exclusion-{hashlib.sha256(seed.encode()).hexdigest()[:32]}",
        "title": title, "year": year, "doi": doi, "openalex_url": openalex_url,
        "reason": reason, "review_note": f"2026-09-05 closed Ant/AI-edit gap audit: {note}",
        "excluded_from_public_preview": "true", "excluded_from_map": "true",
        "is_active": "true", "created_at": now, "created_by": CREATED_BY,
        "source_database": "manual", "metadata_source": "arXiv/publisher",
    })
    rows.append(row)
    temporary = EXCLUSIONS.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAPER_EXCLUSION_COLUMNS, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    temporary.replace(EXCLUSIONS)
    return True


def record_independent_author_review(curated: dict[str, str]) -> bool:
    """Record the explicit non-institutional affiliation without inventing an institution."""
    with INSTITUTION_AUDIT.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        fieldnames = list(reader.fieldnames or ())
    author = "Chenzhuo Zhao"
    if any(
        row.get("action") == "author_affiliation_review"
        and row.get("paper_id") == curated["paper_id"]
        and row.get("affected_authors") == author
        for row in rows
    ):
        return False
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    seed = f"author_affiliation_review|{curated['paper_id']}|{author}|2604.08211"
    row = dict.fromkeys(fieldnames, "")
    row.update({
        "audit_id": f"institution-audit:{hashlib.sha256(seed.encode()).hexdigest()[:20]}",
        "action": "author_affiliation_review", "paper_id": curated["paper_id"],
        "evidence_source": "authoritative arXiv PDF first-page author-affiliation section",
        "evidence_url": "https://arxiv.org/pdf/2604.08211",
        "affected_papers": "1", "affected_authors": author,
        "confirmation_text": json.dumps({
            "status": "non_institutional", "reason_kind": "independent",
            "source_text": "Independent Researcher",
        }, sort_keys=True),
        "review_note": "The paper explicitly identifies Chenzhuo Zhao as an independent researcher; no institution or location entity was created.",
        "created_at": created_at, "created_by": CREATED_BY,
    })
    temporary = INSTITUTION_AUDIT.with_suffix(".csv.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows + [row])
    temporary.replace(INSTITUTION_AUDIT)
    return True


def load_public(path: Path) -> list[dict[str, object]]:
    import json
    return json.loads(path.read_text(encoding="utf-8"))["records"]


def main() -> int:
    entries = read_arxiv_entries()
    public_papers = load_public(PUBLIC_PAPERS)
    public_map = load_public(PUBLIC_MAP)
    curated_rows = read_curated_papers(PAPERS)
    with EXCLUSIONS.open(encoding="utf-8-sig", newline="") as handle:
        exclusion_rows = list(csv.DictReader(handle))
    added = mappings = taxonomy_rows = excluded = independent_reviews = metadata_updates = 0
    for arxiv_id in ADD_IDS:
        draft = paper_draft(arxiv_id, entries[arxiv_id])
        existing = existing_canonical_match(draft, curated_rows)
        if existing is None:
            curated = create_curated_paper(
                draft, preview_records=public_papers,
                exclusion_records=exclusion_rows, path=PAPERS,
            )
            curated_rows.append(curated)
            added += 1
        else:
            curated = dict(existing)
            tasks, scopes, types = LABELS[arxiv_id]
            desired_taxonomy = {
                "tasks": tasks, "image_scopes": scopes, "research_types": types,
            }
            if any(curated.get(key) != value for key, value in desired_taxonomy.items()):
                curated.update(desired_taxonomy)
                curated_rows[curated_rows.index(existing)] = curated
                write_curated_papers(curated_rows, PAPERS)
                metadata_updates += 1
        result = create_mapping_candidates(
            curated, MAPPING_DRAFTS[arxiv_id], map_records=public_map,
            mappings_path=MAPPINGS,
        )
        mappings += len(result["mappings"])
        taxonomy_rows += int(append_taxonomy(curated, arxiv_id, str(entries[arxiv_id]["abstract"])))
        if arxiv_id == "2604.08211":
            independent_reviews += int(record_independent_author_review(curated))
    csiro_reconciled = int(reconcile_csiro_identity())
    synchronize_csiro_location_review()
    kaist_location_created = int(ensure_kaist_location())
    for arxiv_id, (reason, note) in EXCLUDED.items():
        entry = entries[arxiv_id]
        excluded += int(append_exclusion(
            str(entry["title"]), str(entry["published"])[:4], f"10.48550/arxiv.{arxiv_id}",
            f"https://openalex.org/{OPENALEX[arxiv_id]}" if arxiv_id in OPENALEX else "",
            reason, note,
        ))
    excluded += int(append_exclusion(
        "AIGuard: A Benchmark and Lightweight Detection for E-commerce AIGC Risks", "2025",
        "10.18653/v1/2025.findings-acl.643", "", "out_of_scope",
        "AIGC risk/content classification, not generated-image authenticity detection or source attribution.",
    ))
    print(f"papers present: {len(ADD_IDS)}; newly created: {added}")
    print(f"owned paper metadata updates: {metadata_updates}")
    print(f"new mappings: {mappings}; new taxonomy rows: {taxonomy_rows}; new exclusions: {excluded}")
    print(f"new independent-author reviews: {independent_reviews}")
    print(f"CSIRO identity reconciliations: {csiro_reconciled}")
    print(f"KAIST confirmed locations created: {kaist_location_created}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
