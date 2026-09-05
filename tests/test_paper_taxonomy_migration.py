import csv
import json
import unittest
from collections import Counter
from pathlib import Path

from scripts.paper_taxonomy_registry import (
    apply_paper_taxonomy_registry,
    read_paper_taxonomy_registry,
)
from scripts.migrate_paper_taxonomy import build_registry


ROOT = Path(__file__).resolve().parents[1]
SCOPE_EXCLUDED_TITLES = {
    "Can Model Attribution Bridge AI's Accountability Gap in Safety-Critical Domains?",
    "Cascade learning from adversarial synthetic images for accurate pupil detection",
    "DynEval: Holistic Evaluations of T2I Generative Models in the Wild",
    "DeepArt: A Benchmark to Advance Fidelity Research in AI-Generated Content",
    "How spammers and scammers leverage AI-generated images on Facebook for audience growth",
    "Does an emotional connection to art really require a human artist? Emotion and intentionality responses to AI- versus human-created art and impact on aesthetic experience",
}


class PaperTaxonomyMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "data/curated/papers.csv").open(encoding="utf-8", newline="") as handle:
            cls.curated_papers = list(csv.DictReader(handle))
        cls.registry = read_paper_taxonomy_registry(ROOT / "data/curated/paper_taxonomy.csv")
        cls.public = json.loads((ROOT / "web/data/public_preview_papers.json").read_text(encoding="utf-8"))["records"]
        cls.markers = json.loads((ROOT / "web/data/public_preview_map_data.json").read_text(encoding="utf-8"))["records"]

    def test_registry_covers_the_reconciled_public_corpus_not_papers_csv(self):
        self.assertEqual(423, len(self.curated_papers))
        self.assertEqual(613, len(self.registry))
        self.assertEqual(613, len(self.public))
        self.assertEqual(415, sum(bool(row["paper_id"]) for row in self.registry))
        self.assertEqual(198, sum(not row["paper_id"] for row in self.registry))
        summary = apply_paper_taxonomy_registry(
            [dict(row) for row in self.public],
            [dict(row) for row in self.markers],
            self.registry,
        )
        self.assertEqual(613, summary["public_papers_matched"])
        self.assertEqual(1403, summary["map_records_matched"])

    def test_curated_only_exclusions_do_not_enter_registry(self):
        public_ids = {row.get("paper_id") for row in self.public if row.get("paper_id")}
        curated_ids = {row["paper_id"] for row in self.curated_papers}
        curated_only = curated_ids - public_ids
        self.assertEqual(8, len(curated_only))
        self.assertTrue(curated_only.isdisjoint({row["paper_id"] for row in self.registry}))

    def test_focused_scope_exclusions_leave_public_and_taxonomy_outputs(self):
        self.assertTrue(
            SCOPE_EXCLUDED_TITLES.isdisjoint(row["title"] for row in self.registry)
        )
        self.assertTrue(
            SCOPE_EXCLUDED_TITLES.isdisjoint(row["title"] for row in self.public)
        )
        self.assertTrue(
            SCOPE_EXCLUDED_TITLES.isdisjoint(row["title"] for row in self.markers)
        )

    def test_registry_has_independent_dimension_review_evidence(self):
        for row in self.registry:
            for dimension in ("tasks", "image_scopes", "research_types"):
                self.assertIn(row[f"{dimension}_status"], {"reviewed", "needs_review"})
                self.assertTrue(row[f"{dimension}_evidence_tier"])
                self.assertTrue(row[f"{dimension}_evidence_source"])
                self.assertTrue(row[f"{dimension}_evidence_excerpt"])
                if row[f"{dimension}_status"] == "needs_review":
                    self.assertTrue(row[f"{dimension}_review_reason"])
            expected = "needs_review" if any(
                row[f"{dimension}_status"] == "needs_review"
                for dimension in ("tasks", "image_scopes", "research_types")
            ) else "reviewed"
            self.assertEqual(expected, row["taxonomy_status"])

    def test_public_json_uses_arrays_and_exposes_taxonomy_review_separately(self):
        for record in [*self.public, *self.markers]:
            for field in ("tasks", "image_scopes", "research_types"):
                self.assertIsInstance(record.get(field), list)
            self.assertIn(record["taxonomy_status"], {"reviewed", "needs_review"})
            self.assertEqual(
                {"tasks", "image_scopes", "research_types"},
                set(record["taxonomy_review"]),
            )
            self.assertTrue({"task", "paper_categories", "entry_type"}.isdisjoint(record))

    def test_localization_has_explicit_task_or_evaluation_evidence(self):
        localized = [row for row in self.registry if "localization" in row["tasks"].split(";")]
        self.assertEqual(18, len(localized))
        for row in localized:
            evidence = row["tasks_evidence_excerpt"].casefold()
            self.assertTrue("local" in evidence or "segmentation" in evidence, row["title"])

    def test_generative_editing_has_source_modification_evidence(self):
        edited = [row for row in self.registry if "generative_editing" in row["image_scopes"].split(";")]
        self.assertEqual(25, len(edited))
        for row in edited:
            evidence = row["image_scopes_evidence_excerpt"].casefold()
            self.assertTrue(
                any(term in evidence for term in ("inpaint", "edit", "augmented", "stargan", "diffusion")),
                row["title"],
            )

    def test_expected_counts_and_review_counts(self):
        expected = {
            "tasks": Counter(detection=577, source_attribution=77, localization=18),
            "image_scopes": Counter(fully_generated=521, generative_editing=25, deepfake=161, traditional_manipulation=13),
            "research_types": Counter(method=527, dataset=112, benchmark=69, survey=23, analysis_study=58),
        }
        for field, counts in expected.items():
            actual = Counter(value for row in self.registry for value in row[field].split(";") if value)
            self.assertEqual(counts, actual)
        self.assertEqual(
            {"tasks": 0, "image_scopes": 0, "research_types": 0},
            {
                field: sum(row[f"{field}_status"] == "needs_review" for row in self.registry)
                for field in ("tasks", "image_scopes", "research_types")
            },
        )
        self.assertEqual(0, sum(row["taxonomy_status"] == "needs_review" for row in self.registry))

    def test_registry_is_authoritative_on_rerun_including_reviewed_empty_values(self):
        rebuilt = build_registry(
            ROOT / "web/data/public_preview_papers.json",
            ROOT / "data/curated/paper_taxonomy.csv",
        )
        dimensions = ("tasks", "image_scopes", "research_types")
        expected = {row["taxonomy_id"]: row for row in self.registry}
        self.assertEqual(set(expected), {row["taxonomy_id"] for row in rebuilt})
        for row in rebuilt:
            prior = expected[row["taxonomy_id"]]
            for dimension in dimensions:
                self.assertEqual(prior[dimension], row[dimension])
                self.assertEqual(prior[f"{dimension}_status"], row[f"{dimension}_status"])
                self.assertEqual(prior[f"{dimension}_evidence_source"], row[f"{dimension}_evidence_source"])


class FrontendTaxonomyContractTests(unittest.TestCase):
    def test_filters_details_stats_and_deep_links_use_new_dimensions(self):
        html = (ROOT / "web/index.html").read_text(encoding="utf-8")
        app = (ROOT / "web/app.js").read_text(encoding="utf-8")
        for control in ("task-filter", "image-scope-filter", "research-type-filter"):
            self.assertIn(f'id="{control}"', html)
        for parameter in ('"tasks"', '"image_scopes"', '"research_types"'):
            self.assertIn(parameter, app)
        self.assertIn("Dimension counts overlap", app)
        self.assertIn("Paper taxonomy", app)


if __name__ == "__main__":
    unittest.main()
