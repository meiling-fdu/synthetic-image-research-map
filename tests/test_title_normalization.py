import csv
import json
import shutil
import subprocess
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
)


NODE = shutil.which("node") or str(
    Path(
        "/Users/meilinger/.cache/codex-runtimes/"
        "codex-primary-runtime/dependencies/node/bin/node"
    )
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

    def test_admin_metadata_update_normalizes_existing_title_before_saving(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "papers.csv"
            current = normalize_paper_draft(
                {
                    "title": "Temporary Canonical Title",
                    "year": "2025",
                    "authors": "Ada Author",
                    "venue": "Pattern Recognition",
                    "doi": "10.1000/metadata-update",
                    "publication_type": "journal",
                    "task": "detection",
                    "paper_categories": ["method"],
                    "source_database": "manual",
                    "scope_status": "in_scope",
                }
            )
            current.update(
                {
                    "paper_id": "curated:metadata-update",
                    "title": "AI-generated image detection with GenImage",
                    "created_at": "",
                    "updated_at": "",
                }
            )
            write_curated_papers([current], path)

            updated = update_curated_paper(
                current,
                {"abstract": "Updated without resubmitting the title."},
                preview_records=[],
                path=path,
            )

            with path.open(encoding="utf-8", newline="") as handle:
                stored = next(csv.DictReader(handle))
            self.assertEqual(updated["title"], stored["title"])
            self.assertEqual(
                stored["title"],
                "AI-Generated Image Detection with GenImage",
            )

    def test_public_frontend_renders_the_stored_title_without_recasing(self):
        root = Path(__file__).resolve().parents[1]
        app_source = (root / "web/app.js").read_text(encoding="utf-8")
        export_source = (root / "scripts/export_public_preview.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("canonical_paper_title", export_source)
        self.assertNotIn("normalize_record_titles", export_source)
        start = app_source.index("function recordTitle(record)")
        end = app_source.index("\n}\n", start) + 2
        record_title_source = app_source[start:end]
        self.assertIn("TitleMarkup.toHtml(recordTitle(record), escapeHtml)", app_source)
        stored_title = "A deliberately Lowercase Token with AI"
        script = "\n".join(
            (
                record_title_source,
                f"const record = {json.dumps({'title': stored_title})};",
                "process.stdout.write(recordTitle(record));",
            )
        )

        completed = subprocess.run(
            [NODE, "-e", script],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.stdout, stored_title)

    def test_all_current_admin_records_are_canonical(self):
        root = Path(__file__).resolve().parents[1]
        with (root / "data/curated/papers.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            datasets = [("curated papers", list(csv.DictReader(handle)))]
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
