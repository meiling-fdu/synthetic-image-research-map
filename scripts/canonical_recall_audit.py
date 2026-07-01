import json
import random
from pathlib import Path

# ========= CONFIG =========
PUBLIC_PAPERS = Path("web/data/public_preview_papers.json")
MAP_DATA = Path("web/data/public_preview_map_data.json")

SAMPLE_SIZE = 30  # 可调大 50/100

# ========= LOAD =========
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_papers():
    data = load_json(PUBLIC_PAPERS)

    # 支持两种结构
    if isinstance(data, dict) and "records" in data:
        return data["records"]
    return data

def extract_map_records():
    data = load_json(MAP_DATA)
    if isinstance(data, dict) and "records" in data:
        return data["records"]
    return data

# ========= INDEX =========
def build_index(papers):
    doi_index = {}
    title_index = {}

    for p in papers:
        doi = p.get("doi")
        title = p.get("title")

        if doi:
            doi_index[doi.lower()] = p
        if title:
            title_index[title.lower()] = p

    return doi_index, title_index

# ========= AUDIT =========
def audit_sample(candidate_pool, doi_index, title_index):
    missing = []
    hit = []

    sample = random.sample(candidate_pool, min(SAMPLE_SIZE, len(candidate_pool)))

    for item in sample:
        doi = item.get("doi", "").lower()
        title = item.get("title", "").lower()

        found = False

        if doi and doi in doi_index:
            found = True
        elif title and title in title_index:
            found = True

        if found:
            hit.append(item)
        else:
            missing.append(item)

    return hit, missing

# ========= MAIN =========
if __name__ == "__main__":
    papers = extract_papers()
    doi_index, title_index = build_index(papers)

    # 构造“candidate-like pool”（用当前 map + paper 混合检查）
    map_data = extract_map_records()

    # 合并作为“应存在的理论全集”
    candidate_pool = []

    for p in map_data:
        candidate_pool.append(p)

    for p in papers:
        candidate_pool.append(p)

    print(f"\nTotal papers (canonical): {len(papers)}")
    print(f"Total map records: {len(map_data)}")
    print(f"Sampling size: {SAMPLE_SIZE}")

    hit, missing = audit_sample(candidate_pool, doi_index, title_index)

    print("\n================ RESULTS ================")
    print(f"Matched (found in canonical): {len(hit)}")
    print(f"Missing (NOT found): {len(missing)}")

    if missing:
        print("\n🚨 POSSIBLE LOST RECORDS:")
        for m in missing[:20]:
            print("-", m.get("title"), "| DOI:", m.get("doi"))

    print("\n========================================")