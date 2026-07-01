import json
import csv

CANONICAL_PATH = "web/data/public_preview_papers.json"
OPENALEX_PATH = "data/processed/openalex_candidate_papers_in_scope.csv"

# ---------- load canonical ----------
with open(CANONICAL_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

canon = data.get("records", []) if isinstance(data, dict) else data

canon_dois = set()
canon_titles = set()

for r in canon:
    if r.get("doi"):
        canon_dois.add(r["doi"].lower().strip())
    if r.get("title"):
        canon_titles.add(r["title"].lower().strip())

# ---------- load openalex ----------
openalex_dois = set()
openalex_titles = set()

with open(OPENALEX_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        doi = row.get("doi", "")
        title = row.get("title", "")

        if doi:
            openalex_dois.add(doi.lower().strip())
        if title:
            openalex_titles.add(title.lower().strip())

# ---------- diff ----------
missing_doi = openalex_dois - canon_dois
missing_title = openalex_titles - canon_titles

print("\n========== RESULT ==========\n")
print("OpenAlex DOIs:", len(openalex_dois))
print("Canonical DOIs:", len(canon_dois))

print("\nMissing DOI count:", len(missing_doi))
for x in list(missing_doi)[:20]:
    print(" -", x)

print("\nMissing Title count:", len(missing_title))
for x in list(missing_title)[:20]:
    print(" -", x)

print("\n===========================\n")