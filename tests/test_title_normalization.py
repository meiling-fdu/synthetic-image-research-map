import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.curated_papers import (
    normalize_paper_draft,
    update_curated_paper,
    write_curated_papers,
)
from scripts.curated_schema import PAPERS_COLUMNS
from scripts.migrate_paper_titles import migrate_titles
from scripts.title_normalization import (
    canonical_paper_title,
    normalize_record_titles,
)


class TitleNormalizationTests(unittest.TestCase):
    def test_sentence_case_and_technical_tokens(self):
        self.assertEqual(
            canonical_paper_title(
                "AI-generated image detection algorithm based on "
                "classical-quantum hybrid neural network"
            ),
            "AI-Generated Image Detection Algorithm Based on "
            "Classical-Quantum Hybrid Neural Network",
        )

    def test_acronyms_models_and_dataset_styling_are_preserved(self):
        self.assertEqual(
            canonical_paper_title(
                "detecting AIGC with CLIP and LoRA on GenImage"
            ),
            "Detecting AIGC with CLIP and LoRA on GenImage",
        )

    def test_subtitle_edges_and_stop_words(self):
        self.assertEqual(
            canonical_paper_title(
                "from pixels to provenance: a method for detection via AI"
            ),
            "From Pixels to Provenance: A Method for Detection via AI",
        )

    def test_already_correct_title_is_unchanged(self):
        title = "Diffusion Models for AI-Generated Image Detection"
        self.assertEqual(canonical_paper_title(title), title)

    def test_punctuation_unicode_and_spacing_are_unchanged(self):
        source = "weakly‐aligned  image–language detection: an overview"
        result = canonical_paper_title(source)
        self.assertEqual(
            result,
            "Weakly‐Aligned  Image–Language Detection: An Overview",
        )
        self.assertEqual(
            [character for character in result if not character.isalpha()],
            [character for character in source if not character.isalpha()],
        )

    def test_markup_escapes_and_all_caps_author_styling_are_preserved(self):
        self.assertEqual(
            canonical_paper_title(
                "D <sup>3</sup> QE: detection\\n with <scp>AI</scp>"
            ),
            "D <sup>3</sup> QE: Detection\\n with <scp>AI</scp>",
        )
        title = "A COMPARATIVE REVIEW OF AI-GENERATED IMAGE DETECTION"
        self.assertEqual(canonical_paper_title(title), title)

    def test_hyphenated_compound_start_is_capitalized(self):
        self.assertEqual(
            canonical_paper_title("automated in-the-wild detection"),
            "Automated In-the-Wild Detection",
        )

    def test_public_record_normalization_updates_papers_and_markers(self):
        records = [
            {"title": "a detector for AI-generated images"},
            {"title": "Already Correct"},
        ]
        self.assertEqual(normalize_record_titles(records), 1)
        self.assertEqual(records[0]["title"], "A Detector for AI-Generated Images")

    def test_explicit_title_migration_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            papers_path = root / "papers.csv"
            audit_path = root / "audit.csv"
            row = {column: "" for column in PAPERS_COLUMNS}
            row.update(
                {
                    "paper_id": "curated:test",
                    "title": "an image detector with GAN features",
                    "year": "2025",
                }
            )
            with papers_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle, fieldnames=PAPERS_COLUMNS, lineterminator="\n"
                )
                writer.writeheader()
                writer.writerow(row)
            total, changed = migrate_titles(papers_path, audit_path)
            self.assertEqual((total, changed), (1, 1))
            with papers_path.open(encoding="utf-8") as handle:
                stored = next(csv.DictReader(handle))
            self.assertEqual(
                stored["title"], "An Image Detector with GAN Features"
            )
            with audit_path.open(encoding="utf-8") as handle:
                audit = next(csv.DictReader(handle))
            self.assertEqual(audit["changed"], "true")
            first_papers = papers_path.read_bytes()
            first_audit = audit_path.read_bytes()
            self.assertEqual(migrate_titles(papers_path, audit_path), (1, 1))
            self.assertEqual(papers_path.read_bytes(), first_papers)
            self.assertEqual(audit_path.read_bytes(), first_audit)

    def test_admin_create_and_edit_normalize_the_canonical_title(self):
        created = normalize_paper_draft(
            {
                "title": "a survey of AI-generated images",
                "year": "2025",
                "authors": "Ada Author",
                "venue": "Pattern Recognition",
                "doi": "10.1000/title-case",
                "publication_type": "journal",
                "task": "detection",
                "paper_categories": ["method"],
                "source_database": "manual",
                "scope_status": "in_scope",
            }
        )
        self.assertEqual(created["title"], "A Survey of AI-Generated Images")

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "papers.csv"
            current = {
                "paper_id": "curated:title-case",
                **created,
                "created_at": "",
                "updated_at": "",
            }
            write_curated_papers([current], path)
            updated = update_curated_paper(
                current,
                {"title": "detection with CLIP: a practical guide"},
                preview_records=[],
                path=path,
            )
            self.assertEqual(
                updated["title"], "Detection with CLIP: A Practical Guide"
            )

    def test_all_current_admin_and_public_records_are_canonical(self):
        root = Path(__file__).resolve().parents[1]
        with (root / "data/curated/papers.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            datasets = [("curated papers", list(csv.DictReader(handle)))]
        for filename in (
            "public_preview_papers.json",
            "public_preview_map_data.json",
        ):
            with (root / "web/data" / filename).open(encoding="utf-8") as handle:
                datasets.append((filename, json.load(handle)["records"]))
        for dataset_name, records in datasets:
            with self.subTest(dataset=dataset_name):
                self.assertEqual(
                    [
                        record.get("title", "")
                        for record in records
                        if record.get("title", "")
                        != canonical_paper_title(record.get("title", ""))
                    ],
                    [],
                )
