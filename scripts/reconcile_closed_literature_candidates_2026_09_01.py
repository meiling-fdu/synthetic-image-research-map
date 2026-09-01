#!/usr/bin/env python3
"""Apply evidence-backed refreshes from the closed 26-candidate reconciliation."""

from __future__ import annotations

import json
from pathlib import Path

from curated_mappings import create_mapping_candidates
from curated_papers import update_curated_paper


ROOT = Path(__file__).resolve().parents[1]
PAPERS_PATH = ROOT / "data/curated/papers.csv"
PUBLIC_PAPERS_PATH = ROOT / "web/data/public_preview_papers.json"
PUBLIC_MAP_PATH = ROOT / "web/data/public_preview_map_data.json"
LOTA_DOI = "10.1109/iccv51701.2025.01602"
LOTA_PDF = (
    "https://openaccess.thecvf.com/content/ICCV2025/papers/"
    "Wang_LOTA_Bit-Planes_Guided_AI-Generated_Image_Detection_ICCV_2025_paper.pdf#page=1"
)


def records(path: Path) -> list[dict[str, object]]:
    return list(json.loads(path.read_text(encoding="utf-8"))["records"])


def mapping(
    institution: str,
    institution_id: str,
    authors: list[str],
    author_order: str,
    affiliation_order: str,
    raw_affiliation: str,
    city: str,
) -> dict[str, object]:
    return {
        "institution": institution,
        "institution_id": institution_id,
        "institution_authors": authors,
        "author_order": author_order,
        "affiliation_order": affiliation_order,
        "raw_affiliation": raw_affiliation,
        "institution_city": city,
        "institution_country": "China",
        "provenance_source": LOTA_PDF,
        "mapping_status": "active",
    }


def main() -> int:
    public_papers = records(PUBLIC_PAPERS_PATH)
    public_map = records(PUBLIC_MAP_PATH)
    current = next(row for row in public_papers if row.get("doi") == LOTA_DOI)
    curated = update_curated_paper(
        current,
        {
            "title": "LOTA: Bit-Planes Guided AI-Generated Image Detection",
            "authors": [
                "Hongsong Wang",
                "Renxi Cheng",
                "Yang Zhang",
                "Chaolei Han",
                "Jie Gui",
            ],
            "year": "2025",
            "venue_id": "venue:iccv",
            "venue_name": "IEEE/CVF International Conference on Computer Vision",
            "venue": "IEEE/CVF International Conference on Computer Vision",
            "venue_acronym": "ICCV",
            "venue_type": "conference",
            "venue_track": "Main",
            # Preserve the pre-existing OpenAlex raw venue evidence. This pass
            # refreshes the author roster, not the publication identity.
            "raw_venue": "2025 IEEE/CVF International Conference on Computer Vision (ICCV)",
            "replace_raw_venue": True,
            "publication_type": "conference",
            "doi": LOTA_DOI,
            "arxiv_id": "2510.14230",
            "task": "detection",
            "paper_categories": ["method"],
            "scope_status": "in_scope",
            "review_status": "reviewed",
            "curation_status": "confirmed",
        },
        preview_records=public_papers,
        path=PAPERS_PATH,
    )
    result = create_mapping_candidates(
        curated,
        [
            mapping(
                "Southeast University",
                "institution:592f613084a7ca9d",
                ["Hongsong Wang", "Renxi Cheng", "Chaolei Han", "Jie Gui"],
                "1; 2; 4; 5",
                "1",
                "Southeast University, Nanjing, China",
                "Nanjing",
            ),
            mapping(
                "Shenzhen University",
                "institution:ad9c8964d01f80d8",
                ["Yang Zhang"],
                "3",
                "2",
                "School of Computer Science and Software Engineering, Shenzhen University, Shenzhen, China",
                "Shenzhen",
            ),
        ],
        map_records=public_map,
    )
    print(f"LOTA paper identity refreshed: {curated['paper_id']}")
    print(f"Corrected existing relationship rosters created: {len(result['mappings'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
