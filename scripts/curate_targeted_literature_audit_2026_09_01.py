#!/usr/bin/env python3
"""Apply the reviewed 2026-09-01 targeted literature coverage decisions."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from curated_mappings import create_mapping_candidates
from curated_papers import (
    create_curated_paper,
    read_curated_papers,
    update_curated_paper,
)


ROOT = Path(__file__).resolve().parents[1]
PAPERS_PATH = ROOT / "data/curated/papers.csv"
EXCLUSIONS_PATH = ROOT / "data/curated/paper_exclusions.csv"
PUBLIC_PAPERS_PATH = ROOT / "web/data/public_preview_papers.json"
PUBLIC_MAP_PATH = ROOT / "web/data/public_preview_map_data.json"
INSTITUTION_AUDIT_PATH = ROOT / "data/curated/institution_audit_log.csv"

NEURIPS = "Advances in Neural Information Processing Systems"
ACM_MM = "ACM International Conference on Multimedia"
CVPR = "IEEE/CVF Conference on Computer Vision and Pattern Recognition"


def paper(
    title: str,
    authors: list[str],
    venue: str,
    doi: str,
    arxiv_id: str,
    openalex_url: str,
    paper_url: str,
    abstract: str,
) -> dict[str, object]:
    return {
        "title": title,
        "year": "2026" if venue == CVPR else "2025",
        "authors": authors,
        "venue": venue,
        "doi": doi,
        "arxiv_id": arxiv_id,
        "openalex_url": openalex_url,
        "paper_url": paper_url,
        "publication_type": "conference",
        "abstract": abstract,
        "task": "detection",
        "scope_status": "in_scope",
        "source_database": "manual",
        "review_status": "reviewed",
        "paper_categories": ["method"],
    }


PAPERS = [
    paper(
        "Detecting Generated Images by Fitting Natural Image Distributions",
        ["Yonggang Zhang", "Jun Nie", "Xinmei Tian", "Mingming Gong", "Kun Zhang", "Bo Han"],
        NEURIPS,
        "10.52202/085713-1052",
        "2511.01293",
        "https://openalex.org/W4416435591",
        "https://proceedings.neurips.cc/paper_files/paper/2025/hash/2cfa9b0d9be8a5c01cf3eb7f21b4f2b8-Abstract-Conference.html",
        "The increasing realism of generated images has raised significant concerns about their potential misuse, necessitating robust detection methods. Current approaches mainly rely on training binary classifiers, which depend heavily on the quantity and quality of available generated images. This work proposes a framework that exploits geometric differences between the data manifolds of natural and generated images. It employs a pair of functions engineered to yield consistent outputs for natural images but divergent outputs for generated ones, leveraging gradients in mutually orthogonal subspaces. Normalizing flows further amplify detectable differences for advanced generative models.",
    ),
    paper(
        "Denoising Trajectory Biases for Zero-Shot AI-Generated Image Detection",
        ["Yachao Liang", "Min Yu", "Gang Li", "Jianguo Jiang", "Fuqiang Du", "Jingyuan Li", "Lanchi Xie", "Zhen Xu", "Weiqing Huang"],
        NEURIPS,
        "10.52202/085713-5101",
        "",
        "https://openalex.org/W7197012388",
        "https://proceedings.neurips.cc/paper_files/paper/2025/hash/dfd12fe50b18505e3c912c4426707cc7-Abstract-Conference.html",
        "This work introduces a zero-shot AI-generated image detection method based on features in the image generation process. Through diffusion-based inversion, it observes that denoising outputs of generated images converge to the target image more rapidly than those of real images. Similarity between the original image and outputs along the denoising trajectory is used as an authenticity indicator. The method requires no training on generated images and is evaluated across a wide range of generators.",
    ),
    paper(
        "Breaking Latent Prior Bias in Detectors for Generalizable AIGC Image Detection",
        ["Yue Zhou", "Xinan He", "Kaiqing Lin", "Bin Fan", "Feng Ding", "Bin Li"],
        NEURIPS,
        "10.52202/085713-1030",
        "2506.00874",
        "https://openalex.org/W4414893756",
        "https://proceedings.neurips.cc/paper_files/paper/2025/hash/2c2be72635379ec8600eea13df4743e3-Abstract-Conference.html",
        "This work identifies latent-prior bias as one reason AIGC detectors fail to generalize: detectors can learn shortcuts tied to patterns stemming from the initial noise vector. It proposes On-Manifold Adversarial Training, which optimizes initial diffusion noise under fixed conditioning to generate on-manifold adversarial examples. It also introduces the GenImage++ evaluation benchmark and reports improved cross-generator performance without redesigning the detector network.",
    ),
    paper(
        "Epistemic Uncertainty for Generated Image Detection",
        ["Jun Nie", "Yonggang Zhang", "Tongliang Liu", "Yiu-ming Cheung", "Bo Han", "Xinmei Tian"],
        NEURIPS,
        "10.52202/085713-3382",
        "2412.05897",
        "https://openalex.org/W7196944963",
        "https://proceedings.neurips.cc/paper_files/paper/2025/hash/927dfe0d77fb20d9822bacd6737375a8-Abstract-Conference.html",
        "This work frames AI-generated image detection as epistemic uncertainty estimation. Distribution shifts between natural and generated images yield elevated epistemic uncertainty in models trained on natural images. The method uses large-scale vision models pretrained on natural images to estimate uncertainty and flags images with high uncertainty as generated.",
    ),
    paper(
        "Detecting Synthetic Image by Cross-Modal Commonality Interaction",
        ["Kai Li", "Wenqi Ren", "Wei Wang", "Linchao Zhang", "Xiaochun Cao"],
        ACM_MM,
        "10.1145/3746027.3755049",
        "",
        "https://openalex.org/W4415536770",
        "https://doi.org/10.1145/3746027.3755049",
        "This work identifies a shared reliance on high-frequency components across spatial-, frequency-, and fingerprint-based synthetic image detectors. It proposes a multimodal interactive framework combining a high-frequency self-enhancement module, multiscale frequency processing, and pooling-guided cross-modal interaction for general synthetic image detection.",
    ),
    paper(
        "Frequency-aware Correlation Discovering and Spatial Forgery Clue Distilling for Synthetic Image Detection",
        ["Jiehua Zhang", "Liang Li", "Chenggang Yan", "Wei Ke", "Yihong Gong"],
        ACM_MM,
        "10.1145/3746027.3755815",
        "",
        "https://openalex.org/W4415536830",
        "https://doi.org/10.1145/3746027.3755815",
        "This work proposes Gazing Local Detail Forgery for generator-agnostic synthetic image detection. A frequency-aware correlation discovering module learns dynamic filters through instance-adaptive frequency masking, while a spatial forgery clue distilling module iteratively aggregates and refines local dependencies to capture subtle forgery patterns.",
    ),
    paper(
        "Towards Good Generalizations for Diffusion Generated Image Detection Using Multiple Reconstruction Contrastive Learning",
        ["Wanyi Zhuang", "Qi Chu", "Tao Gong", "Changtao Miao", "Nenghai Yu"],
        ACM_MM,
        "10.1145/3746027.3754567",
        "",
        "https://openalex.org/W4415539133",
        "https://doi.org/10.1145/3746027.3754567",
        "This work proposes Multiple Reconstruction Contrastive Learning for diffusion-generated image detection. The method uses multiple VAE reconstruction residuals, a residual dense fusion module, and contrastive learning to improve representation of image origin and cross-generator generalization.",
    ),
    paper(
        "A Difference-in-Difference Approach to Detecting AI-Generated Images",
        ["Xinyi Qi", "Kai Ye", "Chengchun Shi", "Ying Yang", "Jin Zhu", "Hongyi Zhou"],
        CVPR,
        "",
        "2602.23732",
        "",
        "https://openaccess.thecvf.com/content/CVPR2026/html/Qi_A_Difference-in-Difference_Approach_to_Detecting_AI-Generated_Images_CVPR_2026_paper.html",
        "This work proposes a difference-in-difference detector for AI-generated images. Instead of using reconstruction error directly, it computes a second-order difference in reconstruction error to reduce variance and improve detection accuracy as modern synthetic images become increasingly similar to real images.",
    ),
]


PDF_FITTING = "https://proceedings.neurips.cc/paper_files/paper/2025/file/2cfa9b0d9be8a5c01cf3eb7f21b4f2b8-Paper-Conference.pdf#page=1"
PDF_TRAJECTORY = "https://proceedings.neurips.cc/paper_files/paper/2025/file/dfd12fe50b18505e3c912c4426707cc7-Paper-Conference.pdf#page=1"
PDF_LATENT = "https://proceedings.neurips.cc/paper_files/paper/2025/file/2c2be72635379ec8600eea13df4743e3-Paper-Conference.pdf#page=1"
PDF_EPISTEMIC = "https://proceedings.neurips.cc/paper_files/paper/2025/file/927dfe0d77fb20d9822bacd6737375a8-Paper-Conference.pdf#page=1"
PDF_DID = "https://openaccess.thecvf.com/content/CVPR2026/papers/Qi_A_Difference-in-Difference_Approach_to_Detecting_AI-Generated_Images_CVPR_2026_paper.pdf#page=1"


def mapping(institution: str, authors: list[str], order: str, raw: str, source: str, *, institution_id: str = "", city: str = "", country: str = "", openalex_id: str = "", status: str = "active") -> dict[str, str]:
    return {
        "institution": institution,
        "institution_id": institution_id,
        "institution_authors": authors,
        "author_order": order,
        "raw_affiliation": raw,
        "provenance_source": source,
        "institution_city": city,
        "institution_country": country,
        "openalex_institution_id": openalex_id,
        "mapping_status": status,
    }


MAPPINGS = {
    PAPERS[0]["title"]: [
        mapping("The Hong Kong University of Science and Technology", ["Yonggang Zhang"], "1", "The Hong Kong University of Science and Technology", PDF_FITTING, institution_id="institution:fa80d3c071c298e1"),
        mapping("Hong Kong Baptist University", ["Jun Nie", "Bo Han"], "2; 6", "TMLR Group, Hong Kong Baptist University", PDF_FITTING, status="needs_review"),
        mapping("University of Science and Technology of China", ["Jun Nie", "Xinmei Tian"], "2; 3", "University of Science and Technology of China", PDF_FITTING, institution_id="institution:e721b03b6f6c172d"),
        mapping("The University of Melbourne", ["Mingming Gong"], "4", "The University of Melbourne, Australia", PDF_FITTING, country="Australia", status="needs_review"),
        mapping("Carnegie Mellon University", ["Kun Zhang"], "5", "Carnegie Mellon University", PDF_FITTING, institution_id="institution:c5235efb76365de2"),
        mapping("Mohamed bin Zayed University of Artificial Intelligence", ["Mingming Gong", "Kun Zhang"], "4; 5", "Mohamed bin Zayed University of Artificial Intelligence", PDF_FITTING, institution_id="institution:f04b96a9716ab2f4"),
    ],
    PAPERS[1]["title"]: [
        mapping("Institute of Information Engineering, Chinese Academy of Sciences", ["Yachao Liang", "Min Yu", "Jianguo Jiang", "Fuqiang Du", "Zhen Xu", "Weiqing Huang"], "1; 2; 4; 5; 8; 9", "Institute of Information Engineering, Chinese Academy of Sciences", PDF_TRAJECTORY, institution_id="institution:cee70184073782c7"),
        mapping("University of Chinese Academy of Sciences", ["Yachao Liang", "Min Yu", "Jianguo Jiang", "Fuqiang Du", "Zhen Xu", "Weiqing Huang"], "1; 2; 4; 5; 8; 9", "School of Cyber Security, University of Chinese Academy of Sciences", PDF_TRAJECTORY, institution_id="institution:69309405e04976ec"),
        mapping("Deakin University", ["Gang Li"], "3", "Deakin University", PDF_TRAJECTORY, institution_id="institution:30e93da233b7eeef"),
        mapping("Beijing Technology and Business University", ["Jingyuan Li"], "6", "Beijing Technology and Business University", PDF_TRAJECTORY, status="needs_review"),
        mapping("Institute of Forensic Science, Ministry of Public Security", ["Lanchi Xie"], "7", "Institute of Forensic Science, Ministry of Public Security", PDF_TRAJECTORY, status="needs_review"),
    ],
    PAPERS[2]["title"]: [
        mapping("Shenzhen University", ["Yue Zhou", "Kaiqing Lin", "Bin Li"], "1; 3; 6", "Guangdong Provincial Key Laboratory of Intelligent Information Processing, Shenzhen Key Laboratory of Media Security, and SZU-AFS Joint Innovation Center for AI Technology, Shenzhen University", PDF_LATENT, institution_id="institution:ad9c8964d01f80d8"),
        mapping("Nanchang University", ["Xinan He", "Feng Ding"], "2; 5", "Nanchang University", PDF_LATENT, institution_id="institution:74eb5a7db0242865"),
        mapping("University of North Texas", ["Bin Fan"], "4", "University of North Texas", PDF_LATENT, institution_id="institution:f3cfc9b602d85010"),
    ],
    PAPERS[3]["title"]: [
        mapping("University of Science and Technology of China", ["Jun Nie", "Xinmei Tian"], "1; 6", "MoE Key Laboratory of Brain-inspired Intelligent Perception and Cognition, University of Science and Technology of China", PDF_EPISTEMIC, institution_id="institution:e721b03b6f6c172d"),
        mapping("Hong Kong Baptist University", ["Jun Nie", "Yonggang Zhang", "Yiu-ming Cheung", "Bo Han"], "1; 2; 4; 5", "Hong Kong Baptist University", PDF_EPISTEMIC, status="needs_review"),
        mapping("The University of Sydney", ["Tongliang Liu"], "3", "Sydney AI Centre, The University of Sydney", PDF_EPISTEMIC, institution_id="institution:1984e5f97afb62d8"),
        mapping("The Hong Kong University of Science and Technology", ["Yonggang Zhang"], "2", "The Hong Kong University of Science and Technology", PDF_EPISTEMIC, institution_id="institution:fa80d3c071c298e1"),
    ],
    PAPERS[4]["title"]: [
        mapping("Shenzhen Campus of Sun Yat-sen University", ["Kai Li", "Wenqi Ren", "Wei Wang", "Xiaochun Cao"], "1; 2; 3; 5", "Shenzhen Campus of Sun Yat-sen University, Shenzhen, China", "https://api.crossref.org/works/10.1145/3746027.3755049", institution_id="institution:9ab7959736f7be0d", city="Shenzhen", country="China", openalex_id="https://openalex.org/I157773358"),
        mapping("China Electronics Technology Group Corporation", ["Linchao Zhang"], "4", "Artificial Intelligence Institute of China Electronics Technology Group Corporation, Beijing, China", "https://api.crossref.org/works/10.1145/3746027.3755049", institution_id="institution:5757493192522b63", city="Beijing", country="China", openalex_id="https://openalex.org/I2800372957"),
    ],
    PAPERS[5]["title"]: [
        mapping("Xi'an Jiaotong University", ["Jiehua Zhang", "Wei Ke", "Yihong Gong"], "1; 4; 5", "School of Software Engineering / College of Artificial Intelligence, Xi'an Jiaotong University, Xi'an, China", "https://api.crossref.org/works/10.1145/3746027.3755815", institution_id="institution:afc29be68ac419be", city="Xi'an", country="China", openalex_id="https://openalex.org/I87445476"),
        mapping("Institute of Computing Technology, Chinese Academy of Sciences", ["Liang Li"], "2", "Computer Science, Institute of Computing Technology, Chinese Academy of Sciences, Beijing, China", "https://api.crossref.org/works/10.1145/3746027.3755815", institution_id="institution:e278f75918ccf8a7", city="Beijing", country="China", openalex_id="https://openalex.org/I4210090176"),
        mapping("Hangzhou Dianzi University", ["Chenggang Yan"], "3", "Communication Engineering, Hangzhou Dianzi University, Hangzhou, China", "https://api.crossref.org/works/10.1145/3746027.3755815", institution_id="institution:07d62a903f84afcd", city="Hangzhou", country="China", openalex_id="https://openalex.org/I50760025"),
    ],
    PAPERS[6]["title"]: [
        mapping("University of Science and Technology of China", ["Wanyi Zhuang", "Qi Chu", "Tao Gong", "Nenghai Yu"], "1; 2; 3; 5", "University of Science and Technology of China, Hefei, China", "https://api.crossref.org/works/10.1145/3746027.3754567", institution_id="institution:e721b03b6f6c172d", city="Hefei", country="China", openalex_id="https://openalex.org/I126520041"),
    ],
    PAPERS[7]["title"]: [
        mapping("Tsinghua University", ["Xinyi Qi", "Ying Yang", "Hongyi Zhou"], "1; 4; 6", "Tsinghua University, China", PDF_DID, institution_id="institution:4ae45b121fe12e9c", country="China"),
        mapping("London School of Economics and Political Science", ["Kai Ye", "Chengchun Shi"], "2; 3", "LSE, United Kingdom", PDF_DID, country="United Kingdom", status="needs_review"),
        mapping("University of Birmingham", ["Jin Zhu"], "5", "University of Birmingham, United Kingdom", PDF_DID, country="United Kingdom", status="needs_review"),
    ],
}


def load_records(path: Path) -> list[dict[str, object]]:
    return list(json.loads(path.read_text(encoding="utf-8"))["records"])


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def correct_cataid(public_papers: list[dict[str, object]]) -> None:
    current = next(
        row for row in read_curated_papers(PAPERS_PATH)
        if row["title"].startswith("CatAID:")
    )
    update_curated_paper(
        current,
        {
            "venue_id": "venue:iccv",
            "venue_name": "IEEE/CVF International Conference on Computer Vision",
            "venue": "IEEE/CVF International Conference on Computer Vision",
            "venue_acronym": "ICCV",
            "venue_type": "conference",
            "venue_track": "workshops",
            "raw_venue": "2025 IEEE/CVF International Conference on Computer Vision Workshops (ICCVW)",
            "replace_raw_venue": True,
            "publication_type": "conference",
            "review_status": "reviewed",
        },
        preview_records=public_papers,
        path=PAPERS_PATH,
    )


def correct_existing_author_rosters(public_papers: list[dict[str, object]]) -> int:
    """Override three authoritative-name defects without creating public duplicates."""
    corrections = {
        "10.1109/cvpr52734.2025.02219": [
            "Haifeng Zhang", "Qinghui He", "Xiuli Bi", "Weisheng Li", "Bo Liu", "Bin Xiao",
        ],
        "10.48550/arxiv.2311.12397": [
            "Nan Zhong", "Yiran Xu", "Sheng Li", "Zhenxing Qian", "Xinpeng Zhang",
        ],
        "10.1145/3746027.3755142": [
            "Kuo Shi", "Jie Lu", "Shanshan Ye", "Guangquan Zhang", "Zhen Fang",
        ],
    }
    updated = 0
    for doi, authors in corrections.items():
        current = next(row for row in public_papers if row.get("doi") == doi)
        update_curated_paper(
            current,
            {
                "authors": authors,
                "review_status": "reviewed",
                "curation_status": "confirmed",
            },
            preview_records=public_papers,
            path=PAPERS_PATH,
        )
        updated += 1
    return updated


def correct_vib_mapping_roster(
    public_papers: list[dict[str, object]],
    public_map: list[dict[str, object]],
) -> int:
    """Attach the corrected CVF roster to VIB-Net's existing relationship."""
    current = next(
        row for row in public_papers
        if row.get("doi") == "10.1109/cvpr52734.2025.02219"
    )
    result = create_mapping_candidates(
        current,
        [mapping(
            "Chongqing University of Posts and Telecommunications",
            ["Haifeng Zhang", "Qinghui He", "Xiuli Bi", "Weisheng Li", "Bo Liu", "Bin Xiao"],
            "1; 2; 3; 4; 5; 6",
            "Chongqing Key Laboratory of Image Cognition, Chongqing University of Posts and Telecommunications, Chongqing, China",
            "https://openaccess.thecvf.com/content/CVPR2025/papers/Zhang_Towards_Universal_AI-Generated_Image_Detection_by_Variational_Information_Bottleneck_Network_CVPR_2025_paper.pdf#page=1",
            institution_id="institution:7e10613327a4e264",
            city="Chongqing",
            country="China",
            openalex_id="https://openalex.org/I10535382",
        )],
        map_records=public_map,
    )
    return len(result["mappings"])


def record_independent_author_review() -> int:
    """Preserve ACM's explicit Independent affiliation without inventing an entity."""
    with INSTITUTION_AUDIT_PATH.open(encoding="utf-8-sig", newline="") as handle:
        rows = [dict(row) for row in csv.DictReader(handle)]
        fieldnames = list(rows[0])
    paper_id = "curated:54985b9d1db8aeeab8b4"
    author = "Changtao Miao"
    if any(
        row.get("action") == "author_affiliation_review"
        and row.get("paper_id") == paper_id
        and row.get("affected_authors") == author
        for row in rows
    ):
        return 0
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    seed = f"author_affiliation_review|{paper_id}|{author}|10.1145/3746027.3754567"
    row = dict.fromkeys(fieldnames, "")
    row.update({
        "audit_id": f"institution-audit:{hashlib.sha256(seed.encode()).hexdigest()[:20]}",
        "action": "author_affiliation_review",
        "paper_id": paper_id,
        "evidence_source": "ACM publisher-deposited Crossref affiliation metadata",
        "evidence_url": "https://api.crossref.org/works/10.1145/3746027.3754567",
        "affected_papers": "1",
        "affected_authors": author,
        "confirmation_text": json.dumps({
            "status": "non_institutional",
            "reason_kind": "independent",
            "source_text": "Independent, Hangzhou, China",
            "doi": "10.1145/3746027.3754567",
        }, sort_keys=True),
        "review_note": "ACM-deposited affiliation explicitly identifies Changtao Miao as Independent; do not create or geocode an institution.",
        "created_at": created_at,
        "created_by": "codex-targeted-literature-audit-20260901",
    })
    rows.append(row)
    with INSTITUTION_AUDIT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return 1


def main() -> int:
    public_papers = load_records(PUBLIC_PAPERS_PATH)
    public_map = load_records(PUBLIC_MAP_PATH)
    exclusions = load_csv(EXCLUSIONS_PATH)
    correct_cataid(public_papers)
    corrected_rosters = correct_existing_author_rosters(public_papers)
    corrected_vib_mappings = correct_vib_mapping_roster(public_papers, public_map)
    independent_reviews = record_independent_author_review()
    added = []
    mapping_count = 0
    for draft in PAPERS:
        curated = create_curated_paper(
            draft,
            preview_records=public_papers,
            exclusion_records=exclusions,
            path=PAPERS_PATH,
        )
        added.append(curated)
        result = create_mapping_candidates(
            curated,
            MAPPINGS[str(draft["title"])],
            map_records=public_map,
        )
        mapping_count += len(result["mappings"])
    print(f"Curated papers present after audit: {len(added)}")
    print(f"New mappings created: {mapping_count}")
    print("CatAID corrected to ICCV workshops")
    print(f"Existing author rosters corrected: {corrected_rosters}")
    print(f"VIB-Net mapping rosters corrected: {corrected_vib_mappings}")
    print(f"Independent-author reviews recorded: {independent_reviews}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
