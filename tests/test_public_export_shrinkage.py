import json
import tempfile
import unittest
from pathlib import Path

from scripts.export_public_preview import PreviewExportError, enforce_export_baseline
from scripts.public_export_guard import analyze_shrinkage, filter_preserved_records


def paper(
    title="Paper",
    *,
    paper_id="curated:paper",
    doi="10.1000/paper",
    openalex_url="https://openalex.org/W1",
    year=2024,
    arxiv_id="",
):
    return {
        "paper_id": paper_id,
        "title": title,
        "doi": doi,
        "openalex_url": openalex_url,
        "year": year,
        "arxiv_id": arxiv_id,
    }


def marker(paper_record, institution_id="institution:one", institution="One"):
    return {
        **paper_record,
        "institution_id": institution_id,
        "institution": institution,
    }


def exclusion(paper_record, *, active=True):
    return {
        **paper_record,
        "exclusion_id": "exclusion-1",
        "reason": "out_of_scope",
        "is_active": "true" if active else "false",
        "restored_at": "2026-07-17T23:00:57Z" if not active else "",
    }


def merge_row(canonical, duplicate):
    return {
        "merge_id": "merge-1",
        "canonical_title": canonical["title"],
        "canonical_year": str(canonical["year"]),
        "canonical_doi": canonical["doi"],
        "canonical_arxiv_id": canonical.get("arxiv_id", ""),
        "canonical_openalex_url": canonical["openalex_url"],
        "duplicate_title": duplicate["title"],
        "duplicate_year": str(duplicate["year"]),
        "duplicate_doi": duplicate["doi"],
        "duplicate_arxiv_id": duplicate.get("arxiv_id", ""),
        "duplicate_arxiv_url": "",
        "duplicate_openalex_url": duplicate["openalex_url"],
        "status": "confirmed_duplicate",
        "is_active": "true",
    }


class PublicExportShrinkageTests(unittest.TestCase):
    def write_baseline(
        self, directory: str, papers: int, maps: int, name: str = "baseline.json"
    ) -> Path:
        path = Path(directory) / name
        path.write_text(
            json.dumps({"paper_records": papers, "map_records": maps}),
            encoding="utf-8",
        )
        return path

    def test_bootstrap_counts_at_or_above_baseline_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = self.write_baseline(directory, 488, 950)
            enforce_export_baseline(488, 950, baseline)

    def test_public_growth_above_bootstrap_baseline_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = self.write_baseline(directory, 488, 950)
            enforce_export_baseline(500, 1000, baseline)

    def test_bootstrap_unapproved_shrinkage_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = self.write_baseline(directory, 488, 950)
            with self.assertRaisesRegex(PreviewExportError, "shrinkage guard"):
                enforce_export_baseline(395, 703, baseline)

    def test_explicit_approved_baseline_allows_exceptional_reduction(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = self.write_baseline(directory, 488, 950)
            approved = self.write_baseline(directory, 395, 703, "approved.json")
            enforce_export_baseline(395, 703, baseline, approved)

    def test_active_exclusion_explains_paper_removal(self):
        old = paper()
        report = analyze_shrinkage([old], [], [], [], exclusion_rows=[exclusion(old)])
        self.assertTrue(report.allowed)
        self.assertIn("active exclusion", report.removed_papers[0].evidence)

    def test_restored_exclusion_is_not_active_evidence(self):
        old = paper()
        report = analyze_shrinkage(
            [old], [], [], [], exclusion_rows=[exclusion(old, active=False)]
        )
        self.assertFalse(report.allowed)
        self.assertEqual(len(report.unexplained), 1)

    def test_preserve_existing_never_restores_active_exclusion(self):
        old = paper()
        kept = filter_preserved_records(
            [old], map_records=False, exclusion_rows=[exclusion(old)], merge_rows=[]
        )
        self.assertEqual(kept, [])

    def test_partial_candidate_snapshot_is_preserved_without_intent(self):
        old = paper()
        kept = filter_preserved_records(
            [old], map_records=False, exclusion_rows=[], merge_rows=[]
        )
        self.assertEqual(kept, [old])

    def test_confirmed_version_merge_is_explained_and_duplicate_not_preserved(self):
        canonical = paper(
            "Published", paper_id="curated:canonical", doi="10.1000/formal",
            openalex_url="https://openalex.org/W2",
        )
        duplicate = paper(
            "Preprint", paper_id="curated:duplicate", doi="10.48550/arxiv.1",
            openalex_url="https://openalex.org/W3", arxiv_id="2401.00001v2",
        )
        merges = [merge_row(canonical, duplicate)]
        report = analyze_shrinkage(
            [canonical, duplicate],
            [canonical],
            [marker(canonical), marker(duplicate)],
            [marker(canonical)],
            merge_rows=merges,
        )
        self.assertTrue(report.allowed)
        self.assertIn("confirmed version merge", report.removed_papers[0].evidence)
        self.assertIn("confirmed version merge", report.removed_maps[0].evidence)
        self.assertEqual(
            filter_preserved_records(
                [duplicate], map_records=False, exclusion_rows=[], merge_rows=merges
            ),
            [],
        )

    def test_unexplained_paper_loss_fails(self):
        report = analyze_shrinkage([paper()], [], [], [])
        self.assertFalse(report.allowed)
        self.assertEqual(report.removed_papers[0].explained, False)

    def test_approved_baseline_can_authorize_uninferable_exception(self):
        report = analyze_shrinkage(
            [paper()], [], [], [], approved_by_baseline=True
        )
        self.assertTrue(report.allowed)
        self.assertEqual(len(report.unexplained), 1)

    def test_map_reduction_following_active_exclusion_is_explained(self):
        old = paper()
        report = analyze_shrinkage(
            [old], [], [marker(old)], [], exclusion_rows=[exclusion(old)]
        )
        self.assertTrue(report.allowed)
        self.assertTrue(report.removed_maps[0].explained)

    def test_unexplained_map_relationship_loss_fails(self):
        old = paper()
        report = analyze_shrinkage(
            [old], [old], [marker(old)], [], exclusion_rows=[]
        )
        self.assertFalse(report.allowed)
        self.assertEqual(len(report.unexplained), 1)

    def test_reviewed_mapping_exclusion_explains_map_loss(self):
        old = paper()
        decision = {
            **old,
            "decision_id": "review-1",
            "institution": "One",
            "action": "exclude_wrong_mapping",
        }
        report = analyze_shrinkage(
            [old], [old], [marker(old)], [], review_decisions=[decision]
        )
        self.assertTrue(report.allowed)
        self.assertIn("reviewed mapping decision", report.removed_maps[0].evidence)

    def test_legion_stale_fallback_requires_reviewed_removal_across_identity_change(self):
        old = paper(
            "LEGION: Learning to Ground and Explain for Synthetic Image Detection",
            paper_id="curated:14272073fa5bc0e301b5",
            doi="https://doi.org/10.1109/iccv51701.2025.01760",
            openalex_url="https://openalex.org/W4414903171",
            year=2025,
            arxiv_id="2503.15264",
        )
        current = {
            **old,
            "paper_id": "doi:10.1109/iccv51701.2025.01760",
        }
        stale_marker = marker(
            old,
            institution_id="institution:985443a2d7239406",
            institution="Beijing Academy of Artificial Intelligence",
        )
        current_marker = marker(
            current,
            institution_id="institution:c107a95b6cb53ac5",
            institution="Shanghai Artificial Intelligence Laboratory",
        )

        unexplained = analyze_shrinkage(
            [old], [current], [stale_marker], [current_marker]
        )
        self.assertFalse(unexplained.allowed)

        decision = {
            **old,
            "decision_id": "review:43632bd5575cb49bb873",
            "institution": "Beijing Academy of Artificial Intelligence",
            "action": "exclude_wrong_mapping",
        }
        explained = analyze_shrinkage(
            [old],
            [current],
            [stale_marker],
            [current_marker],
            review_decisions=[decision],
        )
        self.assertTrue(explained.allowed)
        self.assertEqual(len(explained.removed_papers), 0)
        self.assertEqual(len(explained.removed_maps), 1)
        self.assertIn(decision["decision_id"], explained.removed_maps[0].evidence)

    def test_active_curated_mapping_replacement_explains_old_relationship(self):
        old = paper()
        old_marker = {
            **marker(old),
            "institution_authors": ["Ada Author"],
        }
        replacement = {
            **old,
            "mapping_id": "mapping-1",
            "institution": "Two",
            "institution_id": "institution:two",
            "institution_authors": "Ada Author",
            "mapping_status": "active",
        }
        replacement_marker = marker(
            old, institution_id="institution:two", institution="Two"
        )
        report = analyze_shrinkage(
            [old],
            [old],
            [old_marker],
            [replacement_marker],
            curated_mappings=[replacement],
        )
        self.assertTrue(report.allowed)
        self.assertIn("curated mapping change", report.removed_maps[0].evidence)

    def test_restored_gan_face_paper_regression_fixture_remains_eligible(self):
        restored = paper(
            "GAN Generated Fake Human Face Image Detection",
            paper_id="",
            doi="10.1109/iitcee59897.2024.10467257",
            openalex_url="https://openalex.org/W4392981221",
        )
        history = [exclusion(restored, active=False)]
        self.assertEqual(
            filter_preserved_records(
                [restored], map_records=False, exclusion_rows=history, merge_rows=[]
            ),
            [restored],
        )
        self.assertTrue(
            analyze_shrinkage(
                [restored], [restored], [], [], exclusion_rows=history
            ).allowed
        )


if __name__ == "__main__":
    unittest.main()
