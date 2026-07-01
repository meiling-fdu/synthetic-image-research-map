import csv
import json
from pathlib import Path
from canonical_authorship import build_canonical_authorship

OPENALEX_PATH = Path("data/processed/openalex_candidate_papers_in_scope.csv")
OUTPUT_PATH = Path("web/data/restored_canonical_papers.json")

# --------------------------
# LOAD OPENALEX (NO PANDAS)
# --------------------------
def load_openalex(path: Path):
    papers = []

    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            papers.append({
                "title": row.get("title"),
                "doi": (row.get("doi") or "").strip(),
                "arxiv": row.get("arxiv"),
                "openalex_url": row.get("openalex_url"),
                "authors": (row.get("authors") or "").split(";"),
                "institutions": [
    {
        "institution": x.strip(),
        "canonical_name": x.strip()
    }
    for x in (row.get("institutions") or "").split(";") if x.strip()
]
            })

    return papers


# --------------------------
# CANONICAL RESTORE PIPELINE
# --------------------------
def restore():
    raw_papers = load_openalex(OPENALEX_PATH)

    canonical_set = {}
    restored = []

    for p in raw_papers:
        # build canonical identity
        canonical = build_canonical_authorship(
            p.get("authors") or [],
            p.get("institutions") or []
        )

        doi_key = (p.get("doi") or "").lower().strip()

        # --------------------------
        # DEDUP: DOI-first strategy
        # --------------------------
        if doi_key and doi_key in canonical_set:
            continue

        p["canonical_authorship"] = canonical

        if doi_key:
            canonical_set[doi_key] = True

        restored.append(p)

    return restored


# --------------------------
# EXPORT
# --------------------------
def save(data):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "dataset_type": "restored_openalex_canonical_merge",
                "count": len(data),
                "records": data
            },
            f,
            ensure_ascii=False,
            indent=2
        )


# --------------------------
# MAIN
# --------------------------
if __name__ == "__main__":
    papers = restore()
    save(papers)

    print("=== RESTORE COMPLETE ===")
    print("Total restored papers:", len(papers))
    print("Output:", OUTPUT_PATH)