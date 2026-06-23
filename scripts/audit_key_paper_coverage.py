import csv
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

KEY_PATH = Path("data/manual/key_papers.csv")
OA_PATH = Path("data/processed/openalex_candidate_papers.csv")
CANDIDATE_JSON = Path("web/data/openalex_candidate_map_data.json")
PREVIEW_JSON = Path("web/data/public_preview_map_data.json")
PREVIEW_PAPERS_JSON = Path("web/data/public_preview_papers.json")
OUT_PATH = Path("data/manual/key_paper_coverage_report.csv")

ALLOWED_STATUSES = {
    "covered_as_map_marker",
    "covered_in_public_preview_paper_list",
    "missing_affiliation",
    "missing_coordinates",
    "missing_from_candidate_pool",
    "possible_title_match_failure",
}
ALLOWED_ACTIONS = {
    "no_action",
    "check_public_preview_filter",
    "check_affiliations_coordinates_or_export_rules",
    "check_affiliations_or_import_enrichment",
    "check_coordinates_or_export_rules",
    "manual_title_match_review",
    "manual_or_openalex_title_import_review",
}

def norm_title(s: str) -> str:
    s = (s or "").lower()
    s = s.replace("‐", "-").replace("–", "-").replace("—", "-")
    s = s.replace("real-world", "real world")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())

def load_csv(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_json_records(path):
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return data.get("records", [])

def best_match(target_norm, title_map):
    best_title = ""
    best_score = 0.0
    target_length = len(target_norm)
    target_tokens = set(target_norm.split())
    for nt, title in title_map.items():
        candidate_length = len(nt)
        if not target_length or not candidate_length:
            continue
        length_ratio = min(target_length, candidate_length) / max(
            target_length,
            candidate_length,
        )
        if length_ratio < 0.45:
            continue
        candidate_tokens = set(nt.split())
        overlap = len(target_tokens & candidate_tokens)
        if not overlap:
            continue
        token_ratio = overlap / max(len(target_tokens), len(candidate_tokens))
        if token_ratio < 0.65:
            continue
        score = SequenceMatcher(None, target_norm, nt).ratio()
        if score > best_score:
            best_score = score
            best_title = title
    return best_title, best_score

def make_title_map(rows):
    out = {}
    for r in rows:
        title = r.get("title", "")
        nt = norm_title(title)
        if nt and nt not in out:
            out[nt] = title
    return out

def yesno(x):
    return "yes" if x else "no"

key_rows = load_csv(KEY_PATH)
oa_rows = load_csv(OA_PATH)
candidate_records = load_json_records(CANDIDATE_JSON)
preview_records = load_json_records(PREVIEW_JSON)
preview_paper_records = load_json_records(PREVIEW_PAPERS_JSON)

oa_map = make_title_map(oa_rows)
candidate_map = make_title_map(candidate_records)
preview_map = make_title_map(preview_records)
preview_paper_map = make_title_map(preview_paper_records)

oa_titles = set(oa_map)
candidate_titles = set(candidate_map)
preview_titles = set(preview_map)
preview_paper_titles = set(preview_paper_map)

preview_paper_by_title = {
    norm_title(row.get("title", "")): row
    for row in preview_paper_records
    if norm_title(row.get("title", ""))
}
preview_marker_count_by_title = {}
for row in preview_records:
    nt = norm_title(row.get("title", ""))
    if nt:
        preview_marker_count_by_title[nt] = preview_marker_count_by_title.get(nt, 0) + 1

report = []

for r in key_rows:
    title = r.get("title", "")
    year = r.get("year", "")
    expected_task = r.get("expected_task", "")
    source_doc = r.get("source_doc", "")
    section = r.get("section", "")
    notes = r.get("notes", "")

    nt = norm_title(title)

    in_oa = nt in oa_titles
    in_candidate = nt in candidate_titles
    in_preview_marker = nt in preview_titles
    in_preview_paper = nt in preview_paper_titles
    preview_paper = preview_paper_by_title.get(nt, {})
    missing_affiliation = preview_paper.get("missing_affiliation") is True
    missing_coordinates = preview_paper.get("missing_coordinates") is True
    map_record_count = preview_marker_count_by_title.get(nt, 0)

    best_oa_title, best_oa_score = best_match(nt, oa_map)
    best_preview_title, best_preview_score = best_match(nt, preview_map)
    best_preview_paper_title, best_preview_paper_score = best_match(nt, preview_paper_map)

    possible_title_match = (
        not in_preview_paper
        and not in_preview_marker
        and (
            best_preview_paper_score >= 0.90
            or best_preview_score >= 0.90
            or best_oa_score >= 0.90
        )
    )

    if in_preview_marker:
        missing_stage = "covered_as_map_marker"
        recommended_action = "no_action"
    elif in_preview_paper:
        missing_stage = "covered_in_public_preview_paper_list"
        if missing_affiliation:
            recommended_action = "check_affiliations_or_import_enrichment"
        elif missing_coordinates:
            recommended_action = "check_coordinates_or_export_rules"
        else:
            recommended_action = "check_public_preview_filter"
    elif in_candidate:
        missing_stage = "missing_coordinates"
        recommended_action = "check_public_preview_filter"
    elif in_oa:
        missing_stage = "missing_affiliation"
        recommended_action = "check_affiliations_coordinates_or_export_rules"
    elif possible_title_match:
        missing_stage = "possible_title_match_failure"
        recommended_action = "manual_title_match_review"
    else:
        missing_stage = "missing_from_candidate_pool"
        recommended_action = "manual_or_openalex_title_import_review"

    report.append({
        "title": title,
        "year": year,
        "expected_task": expected_task,
        "source_doc": source_doc,
        "section": section,
        "in_openalex_candidate_papers": yesno(in_oa),
        "in_candidate_map": yesno(in_candidate),
        "in_public_preview": yesno(in_preview_paper),
        "in_public_preview_paper_list": yesno(in_preview_paper),
        "covered_as_map_marker": yesno(in_preview_marker),
        "map_record_count": map_record_count,
        "missing_affiliation": yesno(missing_affiliation),
        "missing_coordinates": yesno(missing_coordinates),
        "missing_stage": missing_stage,
        "coverage_status": missing_stage,
        "recommended_action": recommended_action,
        "best_openalex_title_match": best_oa_title,
        "best_openalex_title_score": f"{best_oa_score:.3f}",
        "best_public_preview_title_match": best_preview_title,
        "best_public_preview_title_score": f"{best_preview_score:.3f}",
        "best_public_preview_paper_title_match": best_preview_paper_title,
        "best_public_preview_paper_title_score": f"{best_preview_paper_score:.3f}",
        "notes": notes,
    })

invalid_statuses = sorted(
    {row["missing_stage"] for row in report} - ALLOWED_STATUSES
)
invalid_actions = sorted(
    {row["recommended_action"] for row in report} - ALLOWED_ACTIONS
)
if invalid_statuses or invalid_actions:
    raise RuntimeError(
        "Unsupported key-paper audit semantics: "
        f"statuses={invalid_statuses}, actions={invalid_actions}"
    )

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
fields = [
    "title",
    "year",
    "expected_task",
    "source_doc",
    "section",
    "in_openalex_candidate_papers",
    "in_candidate_map",
    "in_public_preview",
    "in_public_preview_paper_list",
    "covered_as_map_marker",
    "map_record_count",
    "missing_affiliation",
    "missing_coordinates",
    "missing_stage",
    "coverage_status",
    "recommended_action",
    "best_openalex_title_match",
    "best_openalex_title_score",
    "best_public_preview_title_match",
    "best_public_preview_title_score",
    "best_public_preview_paper_title_match",
    "best_public_preview_paper_title_score",
    "notes",
]

with OUT_PATH.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(report)

from collections import Counter
print("Wrote:", OUT_PATH)
print("key papers:", len(report))
print("by missing_stage:")
for k, v in Counter(r["missing_stage"] for r in report).most_common():
    print(f"  {k}: {v}")
print("by recommended_action:")
for k, v in Counter(r["recommended_action"] for r in report).most_common():
    print(f"  {k}: {v}")
