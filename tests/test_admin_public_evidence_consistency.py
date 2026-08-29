import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.curated_schema import (
    AUTHOR_INSTITUTION_MAPPING_COLUMNS,
    PAPER_EXCLUSION_COLUMNS,
    PAPERS_COLUMNS,
)
from scripts.serve_admin import identity_keys, load_admin_data, marker_for_api


class AdminPublicEvidenceConsistencyTests(unittest.TestCase):
    def test_openalex_paper_id_matches_openalex_url_identity(self):
        mapping = {
            "paper_id": "openalex:W4391019749",
            "doi": "10.1109/access.2024.3356122",
            "title": "CIFAKE: Image Classification and Explainable Identification of AI-Generated Synthetic Images",
            "year": 2024,
        }
        paper = {
            "openalex_url": "https://openalex.org/W4391019749",
            "doi": "10.1109/access.2024.3356122",
            "title": mapping["title"],
            "year": 2024,
        }

        self.assertTrue(set(identity_keys(mapping)) & set(identity_keys(paper)))

    def test_admin_marker_evidence_is_the_exact_public_map_subset(self):
        paper = {
            "title": "Noise-Informed Diffusion-Generated Image Detection With Anomaly Attention",
            "year": 2025,
            "doi": "10.1109/tifs.2025.3573161",
            "openalex_url": "https://openalex.org/W4410853187",
            "authors": [],
            "affiliation_review_state": "curated",
        }
        public_markers = [
            {
                **paper,
                "id": f"curated-map:{index}",
                "institution": institution,
                "institution_authors": [],
                "source_database": "curated",
                "latitude": 30.0 + index,
                "longitude": 110.0 + index,
            }
            for index, institution in enumerate(
                [
                    "University of Chinese Academy of Sciences",
                    "Institute of Automation, Chinese Academy of Sciences",
                    "Nanjing University of Information Science and Technology",
                    "Communication University of China",
                ],
                start=1,
            )
        ]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            papers_path = root / "public_papers.json"
            maps_path = root / "public_map.json"
            curated_path = root / "papers.csv"
            exclusions_path = root / "paper_exclusions.csv"
            papers_path.write_text(json.dumps({"records": [paper]}), encoding="utf-8")
            maps_path.write_text(
                json.dumps({"records": public_markers}), encoding="utf-8"
            )
            for path, columns in (
                (curated_path, PAPERS_COLUMNS),
                (exclusions_path, PAPER_EXCLUSION_COLUMNS),
            ):
                with path.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=columns)
                    writer.writeheader()

            with (
                patch("scripts.serve_admin.PUBLIC_PAPERS_PATH", papers_path),
                patch("scripts.serve_admin.PUBLIC_MAP_PATH", maps_path),
            ):
                papers, _data = load_admin_data(exclusions_path, curated_path)

        self.assertEqual(len(papers), 1)
        self.assertEqual(
            papers[0]["marker_records"],
            [marker_for_api(marker) for marker in public_markers],
        )

    def test_admin_counts_source_backed_preliminary_public_marker(self):
        paper = {
            "paper_id": "curated:pending",
            "title": "Pending source-backed paper",
            "year": 2026,
            "curation_status": "needs_review",
            "review_status": "pending",
        }
        marker = {
            **paper,
            "id": "curated-map:pending",
            "mapping_id": "mapping:pending",
            "institution": "Example University",
            "institution_id": "institution:example",
            "latitude": 41.9,
            "longitude": 12.5,
            "source_database": "curated",
        }
        mapping = {
            "mapping_id": "mapping:pending",
            "paper_id": paper["paper_id"],
            "title": paper["title"],
            "year": "2026",
            "institution": "Example University",
            "institution_id": "institution:example",
            "institution_authors": "Ada Example",
            "raw_affiliation": "Example University",
            "provenance_source": "paper PDF",
            "mapping_status": "needs_review",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            papers_path = root / "public_papers.json"
            maps_path = root / "public_map.json"
            curated_path = root / "papers.csv"
            exclusions_path = root / "paper_exclusions.csv"
            mappings_path = root / "mappings.csv"
            candidate_path = root / "missing-candidate.json"
            papers_path.write_text(json.dumps({"records": [paper]}), encoding="utf-8")
            maps_path.write_text(json.dumps({"records": [marker]}), encoding="utf-8")
            for path, columns, rows in (
                (curated_path, PAPERS_COLUMNS, []),
                (exclusions_path, PAPER_EXCLUSION_COLUMNS, []),
                (mappings_path, AUTHOR_INSTITUTION_MAPPING_COLUMNS, [mapping]),
            ):
                with path.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=columns)
                    writer.writeheader()
                    writer.writerows(rows)
            with (
                patch("scripts.serve_admin.PUBLIC_PAPERS_PATH", papers_path),
                patch("scripts.serve_admin.PUBLIC_MAP_PATH", maps_path),
            ):
                papers, _data = load_admin_data(
                    exclusions_path,
                    curated_path,
                    mappings_path,
                    candidate_path,
                    apply_venue_audit=False,
                )
        self.assertEqual(papers[0]["map_record_count"], 1)
        self.assertEqual(papers[0]["source_backed_preliminary_mapping_count"], 1)
        self.assertEqual(papers[0]["map_eligible_preliminary_mapping_count"], 1)


if __name__ == "__main__":
    unittest.main()
