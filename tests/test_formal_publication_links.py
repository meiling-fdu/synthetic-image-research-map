import csv
import json
from pathlib import Path

from scripts.paper_links import canonical_url, resolve_public_links


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_LINKS = {
    "curated:5fde2c559e029508e0c3": (
        "https://aclanthology.org/2025.genaidetect-1.2/", "2412.09715"
    ),
    "curated:fb05dfbc95518f6fb1db": (
        "https://openaccess.thecvf.com/content_CVPRW_2019/html/Media_Forensics/"
        "Albright_Source_Generator_Attribution_via_Inversion_CVPRW_2019_paper.html",
        "1905.02259",
    ),
    "curated:7ed4e932c4dac57d0136": (
        "https://openreview.net/forum?id=G5XGej7wNt", "2511.13108"
    ),
    "curated:c87f234ea256991903e1": (
        "https://openreview.net/forum?id=JcjRShiRQz", "2606.10309"
    ),
    "curated:f380c0d31081fc59f1eb": (
        "https://openreview.net/forum?id=qjwFbN77kx", "2606.00606"
    ),
    "curated:078ade9edabe304013a7": (
        "https://openreview.net/forum?id=SzPII70Uta", "2606.07034"
    ),
    "curated:d6fe2666a64b0c70ff6b": (
        "https://openreview.net/forum?id=Fhtwta4397", "2605.16122"
    ),
    "curated:a570863c3a6ac227b56c": (
        "https://openreview.net/forum?id=yEjix8H6Dw", "2605.21207"
    ),
    "curated:4c10e64c5b8f09c7333e": (
        "https://openreview.net/forum?id=7gGl6HB5Zd", "2504.15470"
    ),
    "curated:64635535d7b7b6a12a32": (
        "https://openreview.net/forum?id=Tk8ujiOgHM", "2601.19430"
    ),
    "curated:0400c6b857f88ce96704": (
        "https://openaccess.thecvf.com/content/CVPR2026/html/"
        "Dhakal_SimLBR_Learning_to_Detect_Fake_Images_by_Learning_to_Detect_"
        "CVPR_2026_paper.html",
        "2602.20412",
    ),
}


def records_by_id(path: Path) -> dict[str, dict]:
    if path.suffix == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as handle:
            return {row["paper_id"]: row for row in csv.DictReader(handle)}
    with path.open(encoding="utf-8") as handle:
        return {
            row["paper_id"]: row
            for row in json.load(handle)["records"]
            if row.get("paper_id")
        }


def test_curated_published_and_arxiv_links_are_distinct():
    records = records_by_id(ROOT / "data/curated/papers.csv")
    for paper_id, (published_url, arxiv_id) in EXPECTED_LINKS.items():
        links = resolve_public_links(records[paper_id])
        assert links["formal_url"] == published_url
        assert links["primary_url"] == published_url
        assert links["arxiv_url"] == f"https://arxiv.org/abs/{arxiv_id}"
        assert canonical_url(links["formal_url"]) != canonical_url(links["arxiv_url"])


def test_public_export_preserves_both_version_links():
    records = records_by_id(ROOT / "web/data/public_preview_papers.json")
    for paper_id, (published_url, arxiv_id) in EXPECTED_LINKS.items():
        record = records[paper_id]
        assert record["paper_url"] == published_url
        assert record["formal_url"] == published_url
        assert record["primary_url"] == published_url
        assert record["arxiv_url"] == f"https://arxiv.org/abs/{arxiv_id}"
        assert record["has_arxiv_version"] is True
        assert record["is_arxiv_preprint"] is False
